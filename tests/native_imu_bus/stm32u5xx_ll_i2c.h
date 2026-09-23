// Copies exact installed STM32U585 definitions and selected LL operations.
// Observable four-byte words preserve offsets while modeling hardware side effects.
// Independent B3 native tests exercise the production transfer contract.
#pragma once
/* Copyright (c) 2021 STMicroelectronics. All rights reserved.
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 * Source identities and selected bodies are recorded in extraction.json.
 */
#include "native_cmsis.h"
#define LL_I2C_ICR_ADDRCF                   I2C_ICR_ADDRCF
#define LL_I2C_ICR_NACKCF                   I2C_ICR_NACKCF
#define LL_I2C_ICR_STOPCF                   I2C_ICR_STOPCF
#define LL_I2C_ICR_BERRCF                   I2C_ICR_BERRCF
#define LL_I2C_ICR_ARLOCF                   I2C_ICR_ARLOCF
#define LL_I2C_ICR_OVRCF                    I2C_ICR_OVRCF
#define LL_I2C_ICR_PECCF                    I2C_ICR_PECCF
#define LL_I2C_ICR_TIMOUTCF                 I2C_ICR_TIMOUTCF
#define LL_I2C_ICR_ALERTCF                  I2C_ICR_ALERTCF
#define LL_I2C_ISR_TXE                      I2C_ISR_TXE
#define LL_I2C_ISR_TXIS                     I2C_ISR_TXIS
#define LL_I2C_ISR_RXNE                     I2C_ISR_RXNE
#define LL_I2C_ISR_ADDR                     I2C_ISR_ADDR
#define LL_I2C_ISR_NACKF                    I2C_ISR_NACKF
#define LL_I2C_ISR_STOPF                    I2C_ISR_STOPF
#define LL_I2C_ISR_TC                       I2C_ISR_TC
#define LL_I2C_ISR_TCR                      I2C_ISR_TCR
#define LL_I2C_ISR_BERR                     I2C_ISR_BERR
#define LL_I2C_ISR_ARLO                     I2C_ISR_ARLO
#define LL_I2C_ISR_OVR                      I2C_ISR_OVR
#define LL_I2C_ISR_PECERR                   I2C_ISR_PECERR
#define LL_I2C_ISR_TIMEOUT                  I2C_ISR_TIMEOUT
#define LL_I2C_ISR_ALERT                    I2C_ISR_ALERT
#define LL_I2C_ISR_BUSY                     I2C_ISR_BUSY
#define LL_I2C_CR1_TXIE                     I2C_CR1_TXIE
#define LL_I2C_CR1_RXIE                     I2C_CR1_RXIE
#define LL_I2C_CR1_ADDRIE                   I2C_CR1_ADDRIE
#define LL_I2C_CR1_NACKIE                   I2C_CR1_NACKIE
#define LL_I2C_CR1_STOPIE                   I2C_CR1_STOPIE
#define LL_I2C_CR1_TCIE                     I2C_CR1_TCIE
#define LL_I2C_CR1_ERRIE                    I2C_CR1_ERRIE
#define LL_I2C_MODE_I2C                    0x00000000U
#define LL_I2C_MODE_SMBUS_HOST             I2C_CR1_SMBHEN
#define LL_I2C_MODE_SMBUS_DEVICE           0x00000000U
#define LL_I2C_MODE_SMBUS_DEVICE_ARP       I2C_CR1_SMBDEN
#define LL_I2C_ANALOGFILTER_ENABLE          0x00000000U
#define LL_I2C_ANALOGFILTER_DISABLE         I2C_CR1_ANFOFF
#define LL_I2C_ADDRESSING_MODE_7BIT         0x00000000U
#define LL_I2C_ADDRESSING_MODE_10BIT        I2C_CR2_ADD10
#define LL_I2C_OWNADDRESS1_7BIT             0x00000000U
#define LL_I2C_OWNADDRESS1_10BIT            I2C_OAR1_OA1MODE
#define LL_I2C_OWNADDRESS2_NOMASK           I2C_OAR2_OA2NOMASK
#define LL_I2C_OWNADDRESS2_MASK01           I2C_OAR2_OA2MASK01
#define LL_I2C_OWNADDRESS2_MASK02           I2C_OAR2_OA2MASK02
#define LL_I2C_OWNADDRESS2_MASK03           I2C_OAR2_OA2MASK03
#define LL_I2C_OWNADDRESS2_MASK04           I2C_OAR2_OA2MASK04
#define LL_I2C_OWNADDRESS2_MASK05           I2C_OAR2_OA2MASK05
#define LL_I2C_OWNADDRESS2_MASK06           I2C_OAR2_OA2MASK06
#define LL_I2C_OWNADDRESS2_MASK07           I2C_OAR2_OA2MASK07
#define LL_I2C_ACK                          0x00000000U
#define LL_I2C_NACK                         I2C_CR2_NACK
#define LL_I2C_ADDRSLAVE_7BIT               0x00000000U
#define LL_I2C_ADDRSLAVE_10BIT              I2C_CR2_ADD10
#define LL_I2C_REQUEST_WRITE                0x00000000U
#define LL_I2C_REQUEST_READ                 I2C_CR2_RD_WRN
#define LL_I2C_MODE_RELOAD                  I2C_CR2_RELOAD
#define LL_I2C_MODE_AUTOEND                 I2C_CR2_AUTOEND
#define LL_I2C_MODE_SOFTEND                 0x00000000U
#define LL_I2C_MODE_SMBUS_RELOAD            LL_I2C_MODE_RELOAD
#define LL_I2C_MODE_SMBUS_AUTOEND_NO_PEC    LL_I2C_MODE_AUTOEND
#define LL_I2C_MODE_SMBUS_SOFTEND_NO_PEC    LL_I2C_MODE_SOFTEND
#define LL_I2C_MODE_SMBUS_AUTOEND_WITH_PEC  (uint32_t)(LL_I2C_MODE_AUTOEND | I2C_CR2_PECBYTE)
#define LL_I2C_MODE_SMBUS_SOFTEND_WITH_PEC  (uint32_t)(LL_I2C_MODE_SOFTEND | I2C_CR2_PECBYTE)
#define LL_I2C_GENERATE_NOSTARTSTOP         0x00000000U
#define LL_I2C_GENERATE_STOP                (uint32_t)(0x80000000U | I2C_CR2_STOP)
#define LL_I2C_GENERATE_START_READ          (uint32_t)(0x80000000U | I2C_CR2_START | I2C_CR2_RD_WRN)
#define LL_I2C_GENERATE_START_WRITE         (uint32_t)(0x80000000U | I2C_CR2_START)
#define LL_I2C_GENERATE_RESTART_7BIT_READ   (uint32_t)(0x80000000U | I2C_CR2_START | I2C_CR2_RD_WRN)
#define LL_I2C_GENERATE_RESTART_7BIT_WRITE  (uint32_t)(0x80000000U | I2C_CR2_START)
#define LL_I2C_GENERATE_RESTART_10BIT_READ  (uint32_t)(0x80000000U | I2C_CR2_START | \
                                                       I2C_CR2_RD_WRN | I2C_CR2_HEAD10R)
#define LL_I2C_GENERATE_RESTART_10BIT_WRITE (uint32_t)(0x80000000U | I2C_CR2_START)
#define LL_I2C_DIRECTION_WRITE              0x00000000U
#define LL_I2C_DIRECTION_READ               I2C_ISR_DIR
#define LL_I2C_DMA_REG_DATA_TRANSMIT        0x00000000U
#define LL_I2C_DMA_REG_DATA_RECEIVE         0x00000001U
#define LL_I2C_SMBUS_TIMEOUTA_MODE_SCL_LOW      0x00000000U
#define LL_I2C_SMBUS_TIMEOUTA_MODE_SDA_SCL_HIGH I2C_TIMEOUTR_TIDLE
#define LL_I2C_SMBUS_TIMEOUTA               I2C_TIMEOUTR_TIMOUTEN
#define LL_I2C_SMBUS_TIMEOUTB               I2C_TIMEOUTR_TEXTEN
#define LL_I2C_SMBUS_ALL_TIMEOUT            (uint32_t)(I2C_TIMEOUTR_TIMOUTEN | \
                                                       I2C_TIMEOUTR_TEXTEN)
#define LL_I2C_TRIG_GRP1                   (0x10000000U)
#define LL_I2C_TRIG_GRP2                   (0x20000000U)
#define LL_I2C_GRP1_GPDMA_CH0_TCF_TRG      (uint32_t)(LL_I2C_TRIG_GRP1 | (0x00000000U))
#define LL_I2C_GRP1_GPDMA_CH1_TCF_TRG      (uint32_t)(LL_I2C_TRIG_GRP1 | (0x1U << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP1_GPDMA_CH2_TCF_TRG      (uint32_t)(LL_I2C_TRIG_GRP1 | (0x2U << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP1_GPDMA_CH3_TCF_TRG      (uint32_t)(LL_I2C_TRIG_GRP1 | (0x3U << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP1_EXTI5_TRG              (uint32_t)(LL_I2C_TRIG_GRP1 | (0x4U << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP1_EXTI9_TRG              (uint32_t)(LL_I2C_TRIG_GRP1 | (0x5U << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP1_LPTIM1_CH1_TRG         (uint32_t)(LL_I2C_TRIG_GRP1 | (0x6U << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP1_LPTIM2_CH1_TRG         (uint32_t)(LL_I2C_TRIG_GRP1 | (0x7U << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP1_COMP1_TRG              (uint32_t)(LL_I2C_TRIG_GRP1 | (0x8U << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP1_COMP2_TRG              (uint32_t)(LL_I2C_TRIG_GRP1 | (0x9U << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP1_RTC_ALRA_TRG           (uint32_t)(LL_I2C_TRIG_GRP1 | (0xAU << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP1_RTC_WUT_TRG            (uint32_t)(LL_I2C_TRIG_GRP1 | (0xBU << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP2_LPDMA_CH0_TCF_TRG      (uint32_t)(LL_I2C_TRIG_GRP2 | (0x00000000U))
#define LL_I2C_GRP2_LPDMA_CH1_TCF_TRG      (uint32_t)(LL_I2C_TRIG_GRP2 | (0x1U << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP2_LPDMA_CH2_TCF_TRG      (uint32_t)(LL_I2C_TRIG_GRP2 | (0x2U << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP2_LPDMA_CH3_TCF_TRG      (uint32_t)(LL_I2C_TRIG_GRP2 | (0x3U << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP2_EXTI5_TRG              (uint32_t)(LL_I2C_TRIG_GRP2 | (0x4U << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP2_EXTI8_TRG              (uint32_t)(LL_I2C_TRIG_GRP2 | (0x5U << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP2_LPTIM1_CH1_TRG         (uint32_t)(LL_I2C_TRIG_GRP2 | (0x6U << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP2_LPTIM3_CH1_TRG         (uint32_t)(LL_I2C_TRIG_GRP2 | (0x7U << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP2_COMP1_TRG              (uint32_t)(LL_I2C_TRIG_GRP2 | (0x8U << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP2_COMP2_TRG              (uint32_t)(LL_I2C_TRIG_GRP2 | (0x9U << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP2_RTC_ALRA_TRG           (uint32_t)(LL_I2C_TRIG_GRP2 | (0xAU << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_GRP2_RTC_WUT_TRG            (uint32_t)(LL_I2C_TRIG_GRP2 | (0xBU << I2C_AUTOCR_TRIGSEL_Pos))
#define LL_I2C_TRIG_POLARITY_RISING         0x00000000U
#define LL_I2C_TRIG_POLARITY_FALLING        I2C_AUTOCR_TRIGPOL
#define LL_I2C_WriteReg(__INSTANCE__, __REG__, __VALUE__) WRITE_REG(__INSTANCE__->__REG__, (__VALUE__))
#define LL_I2C_ReadReg(__INSTANCE__, __REG__) READ_REG(__INSTANCE__->__REG__)
inline void LL_I2C_Enable(I2C_TypeDef *I2Cx)
{
  SET_BIT(I2Cx->CR1, I2C_CR1_PE);
}
inline void LL_I2C_Disable(I2C_TypeDef *I2Cx)
{
  CLEAR_BIT(I2Cx->CR1, I2C_CR1_PE);
}
inline uint32_t LL_I2C_IsEnabled(const I2C_TypeDef *I2Cx)
{
  return ((READ_BIT(I2Cx->CR1, I2C_CR1_PE) == (I2C_CR1_PE)) ? 1UL : 0UL);
}
inline void LL_I2C_ConfigFilters(I2C_TypeDef *I2Cx, uint32_t AnalogFilter, uint32_t DigitalFilter)
{
  MODIFY_REG(I2Cx->CR1, I2C_CR1_ANFOFF | I2C_CR1_DNF, AnalogFilter | (DigitalFilter << I2C_CR1_DNF_Pos));
}
inline void LL_I2C_SetTiming(I2C_TypeDef *I2Cx, uint32_t Timing)
{
  WRITE_REG(I2Cx->TIMINGR, Timing);
}
inline void LL_I2C_HandleTransfer(I2C_TypeDef *I2Cx, uint32_t SlaveAddr, uint32_t SlaveAddrSize,
                                           uint32_t TransferSize, uint32_t EndMode, uint32_t Request)
{

  uint32_t tmp = ((uint32_t)(((uint32_t)SlaveAddr & I2C_CR2_SADD) | \
                             ((uint32_t)SlaveAddrSize & I2C_CR2_ADD10) | \
                             (((uint32_t)TransferSize << I2C_CR2_NBYTES_Pos) & I2C_CR2_NBYTES) | \
                             (uint32_t)EndMode | (uint32_t)Request) & (~0x80000000U));


  MODIFY_REG(I2Cx->CR2, I2C_CR2_SADD | I2C_CR2_ADD10 |
             (I2C_CR2_RD_WRN & (uint32_t)(Request >> (31U - I2C_CR2_RD_WRN_Pos))) |
             I2C_CR2_START | I2C_CR2_STOP | I2C_CR2_RELOAD |
             I2C_CR2_NBYTES | I2C_CR2_AUTOEND | I2C_CR2_HEAD10R,
             tmp);
}
inline void LL_I2C_GenerateStopCondition(I2C_TypeDef *I2Cx)
{
  SET_BIT(I2Cx->CR2, I2C_CR2_STOP);
}
inline uint8_t LL_I2C_ReceiveData8(const I2C_TypeDef *I2Cx)
{
  return (uint8_t)(READ_BIT(I2Cx->RXDR, I2C_RXDR_RXDATA));
}
inline void LL_I2C_TransmitData8(I2C_TypeDef *I2Cx, uint8_t Data)
{
  WRITE_REG(I2Cx->TXDR, Data);
}
inline uint32_t LL_I2C_IsActiveFlag_TXE(const I2C_TypeDef *I2Cx)
{
  return ((READ_BIT(I2Cx->ISR, I2C_ISR_TXE) == (I2C_ISR_TXE)) ? 1UL : 0UL);
}
inline uint32_t LL_I2C_IsActiveFlag_TXIS(const I2C_TypeDef *I2Cx)
{
  return ((READ_BIT(I2Cx->ISR, I2C_ISR_TXIS) == (I2C_ISR_TXIS)) ? 1UL : 0UL);
}
inline uint32_t LL_I2C_IsActiveFlag_RXNE(const I2C_TypeDef *I2Cx)
{
  return ((READ_BIT(I2Cx->ISR, I2C_ISR_RXNE) == (I2C_ISR_RXNE)) ? 1UL : 0UL);
}
inline uint32_t LL_I2C_IsActiveFlag_ADDR(const I2C_TypeDef *I2Cx)
{
  return ((READ_BIT(I2Cx->ISR, I2C_ISR_ADDR) == (I2C_ISR_ADDR)) ? 1UL : 0UL);
}
inline uint32_t LL_I2C_IsActiveFlag_NACK(const I2C_TypeDef *I2Cx)
{
  return ((READ_BIT(I2Cx->ISR, I2C_ISR_NACKF) == (I2C_ISR_NACKF)) ? 1UL : 0UL);
}
inline uint32_t LL_I2C_IsActiveFlag_STOP(const I2C_TypeDef *I2Cx)
{
  return ((READ_BIT(I2Cx->ISR, I2C_ISR_STOPF) == (I2C_ISR_STOPF)) ? 1UL : 0UL);
}
inline uint32_t LL_I2C_IsActiveFlag_TC(const I2C_TypeDef *I2Cx)
{
  return ((READ_BIT(I2Cx->ISR, I2C_ISR_TC) == (I2C_ISR_TC)) ? 1UL : 0UL);
}
inline uint32_t LL_I2C_IsActiveFlag_TCR(const I2C_TypeDef *I2Cx)
{
  return ((READ_BIT(I2Cx->ISR, I2C_ISR_TCR) == (I2C_ISR_TCR)) ? 1UL : 0UL);
}
inline uint32_t LL_I2C_IsActiveFlag_BERR(const I2C_TypeDef *I2Cx)
{
  return ((READ_BIT(I2Cx->ISR, I2C_ISR_BERR) == (I2C_ISR_BERR)) ? 1UL : 0UL);
}
inline uint32_t LL_I2C_IsActiveFlag_ARLO(const I2C_TypeDef *I2Cx)
{
  return ((READ_BIT(I2Cx->ISR, I2C_ISR_ARLO) == (I2C_ISR_ARLO)) ? 1UL : 0UL);
}
inline uint32_t LL_I2C_IsActiveFlag_OVR(const I2C_TypeDef *I2Cx)
{
  return ((READ_BIT(I2Cx->ISR, I2C_ISR_OVR) == (I2C_ISR_OVR)) ? 1UL : 0UL);
}
inline uint32_t LL_I2C_IsActiveFlag_BUSY(const I2C_TypeDef *I2Cx)
{
  return ((READ_BIT(I2Cx->ISR, I2C_ISR_BUSY) == (I2C_ISR_BUSY)) ? 1UL : 0UL);
}
inline void LL_I2C_ClearFlag_ADDR(I2C_TypeDef *I2Cx)
{
  SET_BIT(I2Cx->ICR, I2C_ICR_ADDRCF);
}
inline void LL_I2C_ClearFlag_NACK(I2C_TypeDef *I2Cx)
{
  SET_BIT(I2Cx->ICR, I2C_ICR_NACKCF);
}
inline void LL_I2C_ClearFlag_STOP(I2C_TypeDef *I2Cx)
{
  SET_BIT(I2Cx->ICR, I2C_ICR_STOPCF);
}
inline void LL_I2C_ClearFlag_BERR(I2C_TypeDef *I2Cx)
{
  SET_BIT(I2Cx->ICR, I2C_ICR_BERRCF);
}
inline void LL_I2C_ClearFlag_ARLO(I2C_TypeDef *I2Cx)
{
  SET_BIT(I2Cx->ICR, I2C_ICR_ARLOCF);
}
inline void LL_I2C_ClearFlag_OVR(I2C_TypeDef *I2Cx)
{
  SET_BIT(I2Cx->ICR, I2C_ICR_OVRCF);
}
