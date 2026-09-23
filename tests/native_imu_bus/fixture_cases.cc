// Independently checks the native model against installed transfer encodings.
// Fixture errors must be distinguished from production contract failures.
// Exercises repeated START, final RXNE plus STOPF, W1C and command acknowledgement.
#include "doctest.h"
#include "native_fixture.h"
#include "isolation.h"
#include "stm32u5xx_ll_bus.h"
#include <cstddef>
TEST_CASE("B3 fixture retains installed register offsets and exact transfer helpers") {
 fixture::isolated([]{
    fixture::reset();
    CHECK(offsetof(I2C_TypeDef,CR2)==4);CHECK(offsetof(I2C_TypeDef,ISR)==24);
    CHECK(offsetof(I2C_TypeDef,RXDR)==36);CHECK(offsetof(I2C_TypeDef,TXDR)==40);
    LL_APB1_GRP2_EnableClock(LL_APB1_GRP2_PERIPH_I2C4);LL_I2C_Enable(I2C4);
    CHECK(LL_RCC_GetI2CClockSource(LL_RCC_I2C4_CLKSOURCE)==LL_RCC_I2C4_CLKSOURCE_PCLK1);
    LL_I2C_HandleTransfer(I2C4,0xd0,LL_I2C_ADDRSLAVE_7BIT,1,LL_I2C_MODE_SOFTEND,LL_I2C_GENERATE_START_WRITE);
    CHECK((fixture::peek(I2C4->CR2)&I2C_CR2_START)!=0);
    CHECK_FALSE(LL_I2C_IsActiveFlag_TXIS(I2C4));CHECK(LL_I2C_IsActiveFlag_TXIS(I2C4));
    LL_I2C_TransmitData8(I2C4,0x3a);CHECK(LL_I2C_IsActiveFlag_TC(I2C4));
    LL_I2C_HandleTransfer(I2C4,0xd0,LL_I2C_ADDRSLAVE_7BIT,15,LL_I2C_MODE_AUTOEND,LL_I2C_GENERATE_START_READ);
    CHECK_FALSE(LL_I2C_IsActiveFlag_RXNE(I2C4));
    for(unsigned i=0;i<15;++i){REQUIRE(LL_I2C_IsActiveFlag_RXNE(I2C4));
        if(i==14)CHECK((fixture::peek(I2C4->ISR)&I2C_ISR_STOPF)!=0);
        CHECK(LL_I2C_ReceiveData8(I2C4)==fixture::hw.bytes[i]);}
    CHECK(LL_I2C_IsActiveFlag_STOP(I2C4));CHECK_FALSE(LL_I2C_IsActiveFlag_BUSY(I2C4));
    LL_I2C_ClearFlag_STOP(I2C4);CHECK_FALSE(LL_I2C_IsActiveFlag_STOP(I2C4));
    CHECK(fixture::hw.command_errors==0);CHECK(fixture::hw.tx_count==1);CHECK(fixture::hw.rx_count==15);
 });
}
TEST_CASE("B3 fixture can deny pending START and peripheral disable acknowledgements") {
 fixture::isolated([]{
    fixture::reset();LL_APB1_GRP2_EnableClock(LL_APB1_GRP2_PERIPH_I2C4);LL_I2C_Enable(I2C4);
    fixture::hw.start_after=-1;
    LL_I2C_HandleTransfer(I2C4,0xd0,LL_I2C_ADDRSLAVE_7BIT,1,LL_I2C_MODE_SOFTEND,LL_I2C_GENERATE_START_WRITE);
    for(unsigned i=0;i<10;++i){CHECK_FALSE(LL_I2C_IsActiveFlag_TXIS(I2C4));CHECK((fixture::peek(I2C4->CR2)&I2C_CR2_START)!=0);}
    fixture::hw.ignore_disable=true;LL_I2C_Disable(I2C4);CHECK(LL_I2C_IsEnabled(I2C4));
    fixture::hw.ignore_disable=false;LL_I2C_Disable(I2C4);CHECK_FALSE(LL_I2C_IsEnabled(I2C4));
 });
}
TEST_CASE("B3 fixture models hardware configuration lock on each GPIO pin separately") {
 for(unsigned pin:{12U,13U})fixture::isolated([pin]{
    fixture::reset();GPIOD->LCKR.value=GPIO_LCKR_LCKK|(1U<<pin);
    LL_GPIO_SetPinMode(GPIOD,1U<<pin,LL_GPIO_MODE_ALTERNATE);
    LL_GPIO_SetPinPull(GPIOD,1U<<pin,LL_GPIO_PULL_UP);
    LL_GPIO_SetAFPin_8_15(GPIOD,1U<<pin,LL_GPIO_AF_4);
    CHECK(LL_GPIO_GetPinMode(GPIOD,1U<<pin)==LL_GPIO_MODE_ANALOG);
    CHECK(LL_GPIO_GetPinPull(GPIOD,1U<<pin)==LL_GPIO_PULL_NO);
    CHECK(LL_GPIO_GetAFPin_8_15(GPIOD,1U<<pin)==LL_GPIO_AF_0);
    CHECK(fixture::hw.writes==3);
 });
}
