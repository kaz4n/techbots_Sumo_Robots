// Copies the pinned installed STM32U585 UART register shape and bit values.
// Replaces four-byte storage with observed host words to test bounded TX only.
// Source SHA256 8b66d5b9d1514f3ce0950b7a96402e7c026a0779e1cc36c3771be05432b68c06
#pragma once
#include "../../native_qtr/installed_types.h"
#include "../../native_qtr/installed_bits.h"
typedef struct
{
  volatile Reg CR1;
  volatile Reg CR2;
  volatile Reg CR3;
  volatile Reg BRR;
  volatile Reg GTPR;
  volatile Reg RTOR;
  volatile Reg RQR;
  volatile Reg ISR;
  volatile Reg ICR;
  volatile Reg RDR;
  volatile Reg TDR;
  volatile Reg PRESC;
  volatile Reg AUTOCR;
} USART_TypeDef;
#define USART_DMAREQUESTS_SW_WA
#define USART_CR1_UE_Pos                    (0UL)
#define USART_CR1_UE_Msk                    (0x1UL << USART_CR1_UE_Pos)
#define USART_CR1_UE                        USART_CR1_UE_Msk
#define USART_CR1_UESM_Pos                  (1UL)
#define USART_CR1_UESM_Msk                  (0x1UL << USART_CR1_UESM_Pos)
#define USART_CR1_UESM                      USART_CR1_UESM_Msk
#define USART_CR1_RE_Pos                    (2UL)
#define USART_CR1_RE_Msk                    (0x1UL << USART_CR1_RE_Pos)
#define USART_CR1_RE                        USART_CR1_RE_Msk
#define USART_CR1_TE_Pos                    (3UL)
#define USART_CR1_TE_Msk                    (0x1UL << USART_CR1_TE_Pos)
#define USART_CR1_TE                        USART_CR1_TE_Msk
#define USART_CR1_IDLEIE_Pos                (4UL)
#define USART_CR1_IDLEIE_Msk                (0x1UL << USART_CR1_IDLEIE_Pos)
#define USART_CR1_IDLEIE                    USART_CR1_IDLEIE_Msk
#define USART_CR1_RXNEIE_Pos                (5UL)
#define USART_CR1_RXNEIE_Msk                (0x1UL << USART_CR1_RXNEIE_Pos)
#define USART_CR1_RXNEIE                    USART_CR1_RXNEIE_Msk
#define USART_CR1_RXNEIE_RXFNEIE_Pos        USART_CR1_RXNEIE_Pos
#define USART_CR1_RXNEIE_RXFNEIE_Msk        USART_CR1_RXNEIE_Msk
#define USART_CR1_RXNEIE_RXFNEIE            USART_CR1_RXNEIE_Msk
#define USART_CR1_TCIE_Pos                  (6UL)
#define USART_CR1_TCIE_Msk                  (0x1UL << USART_CR1_TCIE_Pos)
#define USART_CR1_TCIE                      USART_CR1_TCIE_Msk
#define USART_CR1_TXEIE_Pos                 (7UL)
#define USART_CR1_TXEIE_Msk                 (0x1UL << USART_CR1_TXEIE_Pos)
#define USART_CR1_TXEIE                     USART_CR1_TXEIE_Msk
#define USART_CR1_TXEIE_TXFNFIE_Pos         (7UL)
#define USART_CR1_TXEIE_TXFNFIE_Msk         (0x1UL << USART_CR1_TXEIE_Pos)
#define USART_CR1_TXEIE_TXFNFIE             USART_CR1_TXEIE
#define USART_CR1_PEIE_Pos                  (8UL)
#define USART_CR1_PEIE_Msk                  (0x1UL << USART_CR1_PEIE_Pos)
#define USART_CR1_PEIE                      USART_CR1_PEIE_Msk
#define USART_CR1_PS_Pos                    (9UL)
#define USART_CR1_PS_Msk                    (0x1UL << USART_CR1_PS_Pos)
#define USART_CR1_PS                        USART_CR1_PS_Msk
#define USART_CR1_PCE_Pos                   (10UL)
#define USART_CR1_PCE_Msk                   (0x1UL << USART_CR1_PCE_Pos)
#define USART_CR1_PCE                       USART_CR1_PCE_Msk
#define USART_CR1_WAKE_Pos                  (11UL)
#define USART_CR1_WAKE_Msk                  (0x1UL << USART_CR1_WAKE_Pos)
#define USART_CR1_WAKE                      USART_CR1_WAKE_Msk
#define USART_CR1_M_Pos                     (12UL)
#define USART_CR1_M_Msk                     (0x10001UL << USART_CR1_M_Pos)
#define USART_CR1_M                         USART_CR1_M_Msk
#define USART_CR1_M0_Pos                    (12UL)
#define USART_CR1_M0_Msk                    (0x1UL << USART_CR1_M0_Pos)
#define USART_CR1_M0                        USART_CR1_M0_Msk
#define USART_CR1_MME_Pos                   (13UL)
#define USART_CR1_MME_Msk                   (0x1UL << USART_CR1_MME_Pos)
#define USART_CR1_MME                       USART_CR1_MME_Msk
#define USART_CR1_CMIE_Pos                  (14UL)
#define USART_CR1_CMIE_Msk                  (0x1UL << USART_CR1_CMIE_Pos)
#define USART_CR1_CMIE                      USART_CR1_CMIE_Msk
#define USART_CR1_OVER8_Pos                 (15UL)
#define USART_CR1_OVER8_Msk                 (0x1UL << USART_CR1_OVER8_Pos)
#define USART_CR1_OVER8                     USART_CR1_OVER8_Msk
#define USART_CR1_DEDT_Pos                  (16UL)
#define USART_CR1_DEDT_Msk                  (0x1FUL << USART_CR1_DEDT_Pos)
#define USART_CR1_DEDT                      USART_CR1_DEDT_Msk
#define USART_CR1_DEDT_0                    (0x01UL << USART_CR1_DEDT_Pos)
#define USART_CR1_DEDT_1                    (0x02UL << USART_CR1_DEDT_Pos)
#define USART_CR1_DEDT_2                    (0x04UL << USART_CR1_DEDT_Pos)
#define USART_CR1_DEDT_3                    (0x08UL << USART_CR1_DEDT_Pos)
#define USART_CR1_DEDT_4                    (0x10UL << USART_CR1_DEDT_Pos)
#define USART_CR1_DEAT_Pos                  (21UL)
#define USART_CR1_DEAT_Msk                  (0x1FUL << USART_CR1_DEAT_Pos)
#define USART_CR1_DEAT                      USART_CR1_DEAT_Msk
#define USART_CR1_DEAT_0                    (0x01UL << USART_CR1_DEAT_Pos)
#define USART_CR1_DEAT_1                    (0x02UL << USART_CR1_DEAT_Pos)
#define USART_CR1_DEAT_2                    (0x04UL << USART_CR1_DEAT_Pos)
#define USART_CR1_DEAT_3                    (0x08UL << USART_CR1_DEAT_Pos)
#define USART_CR1_DEAT_4                    (0x10UL << USART_CR1_DEAT_Pos)
#define USART_CR1_RTOIE_Pos                 (26UL)
#define USART_CR1_RTOIE_Msk                 (0x1UL << USART_CR1_RTOIE_Pos)
#define USART_CR1_RTOIE                     USART_CR1_RTOIE_Msk
#define USART_CR1_EOBIE_Pos                 (27UL)
#define USART_CR1_EOBIE_Msk                 (0x1UL << USART_CR1_EOBIE_Pos)
#define USART_CR1_EOBIE                     USART_CR1_EOBIE_Msk
#define USART_CR1_M1_Pos                    (28UL)
#define USART_CR1_M1_Msk                    (0x1UL << USART_CR1_M1_Pos)
#define USART_CR1_M1                        USART_CR1_M1_Msk
#define USART_CR1_FIFOEN_Pos                (29UL)
#define USART_CR1_FIFOEN_Msk                (0x1UL << USART_CR1_FIFOEN_Pos)
#define USART_CR1_FIFOEN                    USART_CR1_FIFOEN_Msk
#define USART_CR1_TXFEIE_Pos                (30UL)
#define USART_CR1_TXFEIE_Msk                (0x1UL << USART_CR1_TXFEIE_Pos)
#define USART_CR1_TXFEIE                    USART_CR1_TXFEIE_Msk
#define USART_CR1_RXFFIE_Pos                (31UL)
#define USART_CR1_RXFFIE_Msk                (0x1UL << USART_CR1_RXFFIE_Pos)
#define USART_CR1_RXFFIE                    USART_CR1_RXFFIE_Msk
#define USART_CR2_SLVEN_Pos                 (0UL)
#define USART_CR2_SLVEN_Msk                 (0x1UL << USART_CR2_SLVEN_Pos)
#define USART_CR2_SLVEN                     USART_CR2_SLVEN_Msk
#define USART_CR2_DIS_NSS_Pos               (3UL)
#define USART_CR2_DIS_NSS_Msk               (0x1UL << USART_CR2_DIS_NSS_Pos)
#define USART_CR2_DIS_NSS                   USART_CR2_DIS_NSS_Msk
#define USART_CR2_ADDM7_Pos                 (4UL)
#define USART_CR2_ADDM7_Msk                 (0x1UL << USART_CR2_ADDM7_Pos)
#define USART_CR2_ADDM7                     USART_CR2_ADDM7_Msk
#define USART_CR2_LBDL_Pos                  (5UL)
#define USART_CR2_LBDL_Msk                  (0x1UL << USART_CR2_LBDL_Pos)
#define USART_CR2_LBDL                      USART_CR2_LBDL_Msk
#define USART_CR2_LBDIE_Pos                 (6UL)
#define USART_CR2_LBDIE_Msk                 (0x1UL << USART_CR2_LBDIE_Pos)
#define USART_CR2_LBDIE                     USART_CR2_LBDIE_Msk
#define USART_CR2_LBCL_Pos                  (8UL)
#define USART_CR2_LBCL_Msk                  (0x1UL << USART_CR2_LBCL_Pos)
#define USART_CR2_LBCL                      USART_CR2_LBCL_Msk
#define USART_CR2_CPHA_Pos                  (9UL)
#define USART_CR2_CPHA_Msk                  (0x1UL << USART_CR2_CPHA_Pos)
#define USART_CR2_CPHA                      USART_CR2_CPHA_Msk
#define USART_CR2_CPOL_Pos                  (10UL)
#define USART_CR2_CPOL_Msk                  (0x1UL << USART_CR2_CPOL_Pos)
#define USART_CR2_CPOL                      USART_CR2_CPOL_Msk
#define USART_CR2_CLKEN_Pos                 (11UL)
#define USART_CR2_CLKEN_Msk                 (0x1UL << USART_CR2_CLKEN_Pos)
#define USART_CR2_CLKEN                     USART_CR2_CLKEN_Msk
#define USART_CR2_STOP_Pos                  (12UL)
#define USART_CR2_STOP_Msk                  (0x3UL << USART_CR2_STOP_Pos)
#define USART_CR2_STOP                      USART_CR2_STOP_Msk
#define USART_CR2_STOP_0                    (0x1UL << USART_CR2_STOP_Pos)
#define USART_CR2_STOP_1                    (0x2UL << USART_CR2_STOP_Pos)
#define USART_CR2_LINEN_Pos                 (14UL)
#define USART_CR2_LINEN_Msk                 (0x1UL << USART_CR2_LINEN_Pos)
#define USART_CR2_LINEN                     USART_CR2_LINEN_Msk
#define USART_CR2_SWAP_Pos                  (15UL)
#define USART_CR2_SWAP_Msk                  (0x1UL << USART_CR2_SWAP_Pos)
#define USART_CR2_SWAP                      USART_CR2_SWAP_Msk
#define USART_CR2_RXINV_Pos                 (16UL)
#define USART_CR2_RXINV_Msk                 (0x1UL << USART_CR2_RXINV_Pos)
#define USART_CR2_RXINV                     USART_CR2_RXINV_Msk
#define USART_CR2_TXINV_Pos                 (17UL)
#define USART_CR2_TXINV_Msk                 (0x1UL << USART_CR2_TXINV_Pos)
#define USART_CR2_TXINV                     USART_CR2_TXINV_Msk
#define USART_CR2_DATAINV_Pos               (18UL)
#define USART_CR2_DATAINV_Msk               (0x1UL << USART_CR2_DATAINV_Pos)
#define USART_CR2_DATAINV                   USART_CR2_DATAINV_Msk
#define USART_CR2_MSBFIRST_Pos              (19UL)
#define USART_CR2_MSBFIRST_Msk              (0x1UL << USART_CR2_MSBFIRST_Pos)
#define USART_CR2_MSBFIRST                  USART_CR2_MSBFIRST_Msk
#define USART_CR2_ABREN_Pos                 (20UL)
#define USART_CR2_ABREN_Msk                 (0x1UL << USART_CR2_ABREN_Pos)
#define USART_CR2_ABREN                     USART_CR2_ABREN_Msk
#define USART_CR2_ABRMODE_Pos               (21UL)
#define USART_CR2_ABRMODE_Msk               (0x3UL << USART_CR2_ABRMODE_Pos)
#define USART_CR2_ABRMODE                   USART_CR2_ABRMODE_Msk
#define USART_CR2_ABRMODE_0                 (0x1UL << USART_CR2_ABRMODE_Pos)
#define USART_CR2_ABRMODE_1                 (0x2UL << USART_CR2_ABRMODE_Pos)
#define USART_CR2_RTOEN_Pos                 (23UL)
#define USART_CR2_RTOEN_Msk                 (0x1UL << USART_CR2_RTOEN_Pos)
#define USART_CR2_RTOEN                     USART_CR2_RTOEN_Msk
#define USART_CR2_ADD_Pos                   (24UL)
#define USART_CR2_ADD_Msk                   (0xFFUL << USART_CR2_ADD_Pos)
#define USART_CR2_ADD                       USART_CR2_ADD_Msk
#define USART_CR3_EIE_Pos                   (0UL)
#define USART_CR3_EIE_Msk                   (0x1UL << USART_CR3_EIE_Pos)
#define USART_CR3_EIE                       USART_CR3_EIE_Msk
#define USART_CR3_IREN_Pos                  (1UL)
#define USART_CR3_IREN_Msk                  (0x1UL << USART_CR3_IREN_Pos)
#define USART_CR3_IREN                      USART_CR3_IREN_Msk
#define USART_CR3_IRLP_Pos                  (2UL)
#define USART_CR3_IRLP_Msk                  (0x1UL << USART_CR3_IRLP_Pos)
#define USART_CR3_IRLP                      USART_CR3_IRLP_Msk
#define USART_CR3_HDSEL_Pos                 (3UL)
#define USART_CR3_HDSEL_Msk                 (0x1UL << USART_CR3_HDSEL_Pos)
#define USART_CR3_HDSEL                     USART_CR3_HDSEL_Msk
#define USART_CR3_NACK_Pos                  (4UL)
#define USART_CR3_NACK_Msk                  (0x1UL << USART_CR3_NACK_Pos)
#define USART_CR3_NACK                      USART_CR3_NACK_Msk
#define USART_CR3_SCEN_Pos                  (5UL)
#define USART_CR3_SCEN_Msk                  (0x1UL << USART_CR3_SCEN_Pos)
#define USART_CR3_SCEN                      USART_CR3_SCEN_Msk
#define USART_CR3_DMAR_Pos                  (6UL)
#define USART_CR3_DMAR_Msk                  (0x1UL << USART_CR3_DMAR_Pos)
#define USART_CR3_DMAR                      USART_CR3_DMAR_Msk
#define USART_CR3_DMAT_Pos                  (7UL)
#define USART_CR3_DMAT_Msk                  (0x1UL << USART_CR3_DMAT_Pos)
#define USART_CR3_DMAT                      USART_CR3_DMAT_Msk
#define USART_CR3_RTSE_Pos                  (8UL)
#define USART_CR3_RTSE_Msk                  (0x1UL << USART_CR3_RTSE_Pos)
#define USART_CR3_RTSE                      USART_CR3_RTSE_Msk
#define USART_CR3_CTSE_Pos                  (9UL)
#define USART_CR3_CTSE_Msk                  (0x1UL << USART_CR3_CTSE_Pos)
#define USART_CR3_CTSE                      USART_CR3_CTSE_Msk
#define USART_CR3_CTSIE_Pos                 (10UL)
#define USART_CR3_CTSIE_Msk                 (0x1UL << USART_CR3_CTSIE_Pos)
#define USART_CR3_CTSIE                     USART_CR3_CTSIE_Msk
#define USART_CR3_ONEBIT_Pos                (11UL)
#define USART_CR3_ONEBIT_Msk                (0x1UL << USART_CR3_ONEBIT_Pos)
#define USART_CR3_ONEBIT                    USART_CR3_ONEBIT_Msk
#define USART_CR3_OVRDIS_Pos                (12UL)
#define USART_CR3_OVRDIS_Msk                (0x1UL << USART_CR3_OVRDIS_Pos)
#define USART_CR3_OVRDIS                    USART_CR3_OVRDIS_Msk
#define USART_CR3_DDRE_Pos                  (13UL)
#define USART_CR3_DDRE_Msk                  (0x1UL << USART_CR3_DDRE_Pos)
#define USART_CR3_DDRE                      USART_CR3_DDRE_Msk
#define USART_CR3_DEM_Pos                   (14UL)
#define USART_CR3_DEM_Msk                   (0x1UL << USART_CR3_DEM_Pos)
#define USART_CR3_DEM                       USART_CR3_DEM_Msk
#define USART_CR3_DEP_Pos                   (15UL)
#define USART_CR3_DEP_Msk                   (0x1UL << USART_CR3_DEP_Pos)
#define USART_CR3_DEP                       USART_CR3_DEP_Msk
#define USART_CR3_SCARCNT_Pos               (17UL)
#define USART_CR3_SCARCNT_Msk               (0x7UL << USART_CR3_SCARCNT_Pos)
#define USART_CR3_SCARCNT                   USART_CR3_SCARCNT_Msk
#define USART_CR3_SCARCNT_0                 (0x1UL << USART_CR3_SCARCNT_Pos)
#define USART_CR3_SCARCNT_1                 (0x2UL << USART_CR3_SCARCNT_Pos)
#define USART_CR3_SCARCNT_2                 (0x4UL << USART_CR3_SCARCNT_Pos)
#define USART_CR3_TXFTIE_Pos                (23UL)
#define USART_CR3_TXFTIE_Msk                (0x1UL << USART_CR3_TXFTIE_Pos)
#define USART_CR3_TXFTIE                    USART_CR3_TXFTIE_Msk
#define USART_CR3_TCBGTIE_Pos               (24UL)
#define USART_CR3_TCBGTIE_Msk               (0x1UL << USART_CR3_TCBGTIE_Pos)
#define USART_CR3_TCBGTIE                   USART_CR3_TCBGTIE_Msk
#define USART_CR3_RXFTCFG_Pos               (25UL)
#define USART_CR3_RXFTCFG_Msk               (0x7UL << USART_CR3_RXFTCFG_Pos)
#define USART_CR3_RXFTCFG                   USART_CR3_RXFTCFG_Msk
#define USART_CR3_RXFTCFG_0                 (0x1UL << USART_CR3_RXFTCFG_Pos)
#define USART_CR3_RXFTCFG_1                 (0x2UL << USART_CR3_RXFTCFG_Pos)
#define USART_CR3_RXFTCFG_2                 (0x4UL << USART_CR3_RXFTCFG_Pos)
#define USART_CR3_RXFTIE_Pos                (28UL)
#define USART_CR3_RXFTIE_Msk                (0x1UL << USART_CR3_RXFTIE_Pos)
#define USART_CR3_RXFTIE                    USART_CR3_RXFTIE_Msk
#define USART_CR3_TXFTCFG_Pos               (29UL)
#define USART_CR3_TXFTCFG_Msk               (0x7UL << USART_CR3_TXFTCFG_Pos)
#define USART_CR3_TXFTCFG                   USART_CR3_TXFTCFG_Msk
#define USART_CR3_TXFTCFG_0                 (0x1UL << USART_CR3_TXFTCFG_Pos)
#define USART_CR3_TXFTCFG_1                 (0x2UL << USART_CR3_TXFTCFG_Pos)
#define USART_CR3_TXFTCFG_2                 (0x4UL << USART_CR3_TXFTCFG_Pos)
#define USART_BRR_LPUART_Pos                (0UL)
#define USART_BRR_LPUART_Msk                (0xFFFFFUL << USART_BRR_LPUART_Pos)
#define USART_BRR_LPUART                    USART_BRR_LPUART_Msk
#define USART_BRR_BRR                       ((uint16_t)0xFFFF)
#define USART_GTPR_PSC_Pos                  (0UL)
#define USART_GTPR_PSC_Msk                  (0xFFUL << USART_GTPR_PSC_Pos)
#define USART_GTPR_PSC                      USART_GTPR_PSC_Msk
#define USART_GTPR_GT_Pos                   (8UL)
#define USART_GTPR_GT_Msk                   (0xFFUL << USART_GTPR_GT_Pos)
#define USART_GTPR_GT                       USART_GTPR_GT_Msk
#define USART_RTOR_RTO_Pos                  (0UL)
#define USART_RTOR_RTO_Msk                  (0xFFFFFFUL << USART_RTOR_RTO_Pos)
#define USART_RTOR_RTO                      USART_RTOR_RTO_Msk
#define USART_RTOR_BLEN_Pos                 (24UL)
#define USART_RTOR_BLEN_Msk                 (0xFFUL << USART_RTOR_BLEN_Pos)
#define USART_RTOR_BLEN                     USART_RTOR_BLEN_Msk
#define USART_RQR_ABRRQ                     ((uint16_t)0x0001)
#define USART_RQR_SBKRQ                     ((uint16_t)0x0002)
#define USART_RQR_MMRQ                      ((uint16_t)0x0004)
#define USART_RQR_RXFRQ                     ((uint16_t)0x0008)
#define USART_RQR_TXFRQ                     ((uint16_t)0x0010)
#define USART_ISR_PE_Pos                    (0UL)
#define USART_ISR_PE_Msk                    (0x1UL << USART_ISR_PE_Pos)
#define USART_ISR_PE                        USART_ISR_PE_Msk
#define USART_ISR_FE_Pos                    (1UL)
#define USART_ISR_FE_Msk                    (0x1UL << USART_ISR_FE_Pos)
#define USART_ISR_FE                        USART_ISR_FE_Msk
#define USART_ISR_NE_Pos                    (2UL)
#define USART_ISR_NE_Msk                    (0x1UL << USART_ISR_NE_Pos)
#define USART_ISR_NE                        USART_ISR_NE_Msk
#define USART_ISR_ORE_Pos                   (3UL)
#define USART_ISR_ORE_Msk                   (0x1UL << USART_ISR_ORE_Pos)
#define USART_ISR_ORE                       USART_ISR_ORE_Msk
#define USART_ISR_IDLE_Pos                  (4UL)
#define USART_ISR_IDLE_Msk                  (0x1UL << USART_ISR_IDLE_Pos)
#define USART_ISR_IDLE                      USART_ISR_IDLE_Msk
#define USART_ISR_RXNE_Pos                  (5UL)
#define USART_ISR_RXNE_Msk                  (0x1UL << USART_ISR_RXNE_Pos)
#define USART_ISR_RXNE                      USART_ISR_RXNE_Msk
#define USART_ISR_RXNE_RXFNE_Pos            USART_ISR_RXNE_Pos
#define USART_ISR_RXNE_RXFNE_Msk            USART_ISR_RXNE_Msk
#define USART_ISR_RXNE_RXFNE                USART_ISR_RXNE_Msk
#define USART_ISR_TC_Pos                    (6UL)
#define USART_ISR_TC_Msk                    (0x1UL << USART_ISR_TC_Pos)
#define USART_ISR_TC                        USART_ISR_TC_Msk
#define USART_ISR_TXE_Pos                   (7UL)
#define USART_ISR_TXE_Msk                   (0x1UL << USART_ISR_TXE_Pos)
#define USART_ISR_TXE                       USART_ISR_TXE_Msk
#define USART_ISR_TXE_TXFNF_Pos             USART_ISR_TXE_Pos
#define USART_ISR_TXE_TXFNF_Msk             USART_ISR_TXE_Msk
#define USART_ISR_TXE_TXFNF                 USART_ISR_TXE_Msk
#define USART_ISR_LBDF_Pos                  (8UL)
#define USART_ISR_LBDF_Msk                  (0x1UL << USART_ISR_LBDF_Pos)
#define USART_ISR_LBDF                      USART_ISR_LBDF_Msk
#define USART_ISR_CTSIF_Pos                 (9UL)
#define USART_ISR_CTSIF_Msk                 (0x1UL << USART_ISR_CTSIF_Pos)
#define USART_ISR_CTSIF                     USART_ISR_CTSIF_Msk
#define USART_ISR_CTS_Pos                   (10UL)
#define USART_ISR_CTS_Msk                   (0x1UL << USART_ISR_CTS_Pos)
#define USART_ISR_CTS                       USART_ISR_CTS_Msk
#define USART_ISR_RTOF_Pos                  (11UL)
#define USART_ISR_RTOF_Msk                  (0x1UL << USART_ISR_RTOF_Pos)
#define USART_ISR_RTOF                      USART_ISR_RTOF_Msk
#define USART_ISR_EOBF_Pos                  (12UL)
#define USART_ISR_EOBF_Msk                  (0x1UL << USART_ISR_EOBF_Pos)
#define USART_ISR_EOBF                      USART_ISR_EOBF_Msk
#define USART_ISR_UDR_Pos                   (13UL)
#define USART_ISR_UDR_Msk                   (0x1UL << USART_ISR_UDR_Pos)
#define USART_ISR_UDR                       USART_ISR_UDR_Msk
#define USART_ISR_ABRE_Pos                  (14UL)
#define USART_ISR_ABRE_Msk                  (0x1UL << USART_ISR_ABRE_Pos)
#define USART_ISR_ABRE                      USART_ISR_ABRE_Msk
#define USART_ISR_ABRF_Pos                  (15UL)
#define USART_ISR_ABRF_Msk                  (0x1UL << USART_ISR_ABRF_Pos)
#define USART_ISR_ABRF                      USART_ISR_ABRF_Msk
#define USART_ISR_BUSY_Pos                  (16UL)
#define USART_ISR_BUSY_Msk                  (0x1UL << USART_ISR_BUSY_Pos)
#define USART_ISR_BUSY                      USART_ISR_BUSY_Msk
#define USART_ISR_CMF_Pos                   (17UL)
#define USART_ISR_CMF_Msk                   (0x1UL << USART_ISR_CMF_Pos)
#define USART_ISR_CMF                       USART_ISR_CMF_Msk
#define USART_ISR_SBKF_Pos                  (18UL)
#define USART_ISR_SBKF_Msk                  (0x1UL << USART_ISR_SBKF_Pos)
#define USART_ISR_SBKF                      USART_ISR_SBKF_Msk
#define USART_ISR_RWU_Pos                   (19UL)
#define USART_ISR_RWU_Msk                   (0x1UL << USART_ISR_RWU_Pos)
#define USART_ISR_RWU                       USART_ISR_RWU_Msk
#define USART_ISR_TEACK_Pos                 (21UL)
#define USART_ISR_TEACK_Msk                 (0x1UL << USART_ISR_TEACK_Pos)
#define USART_ISR_TEACK                     USART_ISR_TEACK_Msk
#define USART_ISR_REACK_Pos                 (22UL)
#define USART_ISR_REACK_Msk                 (0x1UL << USART_ISR_REACK_Pos)
#define USART_ISR_REACK                     USART_ISR_REACK_Msk
#define USART_ISR_TXFE_Pos                  (23UL)
#define USART_ISR_TXFE_Msk                  (0x1UL << USART_ISR_TXFE_Pos)
#define USART_ISR_TXFE                      USART_ISR_TXFE_Msk
#define USART_ISR_RXFF_Pos                  (24UL)
#define USART_ISR_RXFF_Msk                  (0x1UL << USART_ISR_RXFF_Pos)
#define USART_ISR_RXFF                      USART_ISR_RXFF_Msk
#define USART_ISR_TCBGT_Pos                 (25UL)
#define USART_ISR_TCBGT_Msk                 (0x1UL << USART_ISR_TCBGT_Pos)
#define USART_ISR_TCBGT                     USART_ISR_TCBGT_Msk
#define USART_ISR_RXFT_Pos                  (26UL)
#define USART_ISR_RXFT_Msk                  (0x1UL << USART_ISR_RXFT_Pos)
#define USART_ISR_RXFT                      USART_ISR_RXFT_Msk
#define USART_ISR_TXFT_Pos                  (27UL)
#define USART_ISR_TXFT_Msk                  (0x1UL << USART_ISR_TXFT_Pos)
#define USART_ISR_TXFT                      USART_ISR_TXFT_Msk
#define USART_ICR_PECF_Pos                  (0UL)
#define USART_ICR_PECF_Msk                  (0x1UL << USART_ICR_PECF_Pos)
#define USART_ICR_PECF                      USART_ICR_PECF_Msk
#define USART_ICR_FECF_Pos                  (1UL)
#define USART_ICR_FECF_Msk                  (0x1UL << USART_ICR_FECF_Pos)
#define USART_ICR_FECF                      USART_ICR_FECF_Msk
#define USART_ICR_NECF_Pos                  (2UL)
#define USART_ICR_NECF_Msk                  (0x1UL << USART_ICR_NECF_Pos)
#define USART_ICR_NECF                      USART_ICR_NECF_Msk
#define USART_ICR_ORECF_Pos                 (3UL)
#define USART_ICR_ORECF_Msk                 (0x1UL << USART_ICR_ORECF_Pos)
#define USART_ICR_ORECF                     USART_ICR_ORECF_Msk
#define USART_ICR_IDLECF_Pos                (4UL)
#define USART_ICR_IDLECF_Msk                (0x1UL << USART_ICR_IDLECF_Pos)
#define USART_ICR_IDLECF                    USART_ICR_IDLECF_Msk
#define USART_ICR_TXFECF_Pos                (5UL)
#define USART_ICR_TXFECF_Msk                (0x1UL << USART_ICR_TXFECF_Pos)
#define USART_ICR_TXFECF                    USART_ICR_TXFECF_Msk
#define USART_ICR_TCCF_Pos                  (6UL)
#define USART_ICR_TCCF_Msk                  (0x1UL << USART_ICR_TCCF_Pos)
#define USART_ICR_TCCF                      USART_ICR_TCCF_Msk
#define USART_ICR_TCBGTCF_Pos               (7UL)
#define USART_ICR_TCBGTCF_Msk               (0x1UL << USART_ICR_TCBGTCF_Pos)
#define USART_ICR_TCBGTCF                   USART_ICR_TCBGTCF_Msk
#define USART_ICR_LBDCF_Pos                 (8UL)
#define USART_ICR_LBDCF_Msk                 (0x1UL << USART_ICR_LBDCF_Pos)
#define USART_ICR_LBDCF                     USART_ICR_LBDCF_Msk
#define USART_ICR_CTSCF_Pos                 (9UL)
#define USART_ICR_CTSCF_Msk                 (0x1UL << USART_ICR_CTSCF_Pos)
#define USART_ICR_CTSCF                     USART_ICR_CTSCF_Msk
#define USART_ICR_RTOCF_Pos                 (11UL)
#define USART_ICR_RTOCF_Msk                 (0x1UL << USART_ICR_RTOCF_Pos)
#define USART_ICR_RTOCF                     USART_ICR_RTOCF_Msk
#define USART_ICR_EOBCF_Pos                 (12UL)
#define USART_ICR_EOBCF_Msk                 (0x1UL << USART_ICR_EOBCF_Pos)
#define USART_ICR_EOBCF                     USART_ICR_EOBCF_Msk
#define USART_ICR_UDRCF_Pos                 (13UL)
#define USART_ICR_UDRCF_Msk                 (0x1UL << USART_ICR_UDRCF_Pos)
#define USART_ICR_UDRCF                     USART_ICR_UDRCF_Msk
#define USART_ICR_CMCF_Pos                  (17UL)
#define USART_ICR_CMCF_Msk                  (0x1UL << USART_ICR_CMCF_Pos)
#define USART_ICR_CMCF                      USART_ICR_CMCF_Msk
#define USART_RDR_RDR                       ((uint16_t)0x01FF)
#define USART_TDR_TDR                       ((uint16_t)0x01FF)
#define USART_PRESC_PRESCALER_Pos           (0UL)
#define USART_PRESC_PRESCALER_Msk           (0xFUL << USART_PRESC_PRESCALER_Pos)
#define USART_PRESC_PRESCALER               USART_PRESC_PRESCALER_Msk
#define USART_PRESC_PRESCALER_0             (0x1UL << USART_PRESC_PRESCALER_Pos)
#define USART_PRESC_PRESCALER_1             (0x2UL << USART_PRESC_PRESCALER_Pos)
#define USART_PRESC_PRESCALER_2             (0x4UL << USART_PRESC_PRESCALER_Pos)
#define USART_PRESC_PRESCALER_3             (0x8UL << USART_PRESC_PRESCALER_Pos)
#define USART_AUTOCR_TDN_Pos                (0UL)
#define USART_AUTOCR_TDN_Msk                (0xFFFFUL << USART_AUTOCR_TDN_Pos)
#define USART_AUTOCR_TDN                    USART_AUTOCR_TDN_Msk
#define USART_AUTOCR_TRIGPOL_Pos            (16UL)
#define USART_AUTOCR_TRIGPOL_Msk            (0x1UL << USART_AUTOCR_TRIGPOL_Pos)
#define USART_AUTOCR_TRIGPOL                USART_AUTOCR_TRIGPOL_Msk
#define USART_AUTOCR_TRIGEN_Pos             (17UL)
#define USART_AUTOCR_TRIGEN_Msk             (0x1UL << USART_AUTOCR_TRIGEN_Pos)
#define USART_AUTOCR_TRIGEN                 USART_AUTOCR_TRIGEN_Msk
#define USART_AUTOCR_IDLEDIS_Pos            (18UL)
#define USART_AUTOCR_IDLEDIS_Msk            (0x1UL << USART_AUTOCR_IDLEDIS_Pos)
#define USART_AUTOCR_IDLEDIS                USART_AUTOCR_IDLEDIS_Msk
#define USART_AUTOCR_TRIGSEL_Pos            (19UL)
#define USART_AUTOCR_TRIGSEL_Msk            (0xFUL << USART_AUTOCR_TRIGSEL_Pos)
#define USART_AUTOCR_TRIGSEL                USART_AUTOCR_TRIGSEL_Msk
#define USART_AUTOCR_TRIGSEL_0              (0x0001UL << USART_AUTOCR_TRIGSEL_Pos)
#define USART_AUTOCR_TRIGSEL_1              (0x0002UL << USART_AUTOCR_TRIGSEL_Pos)
#define USART_AUTOCR_TRIGSEL_2              (0x0004UL << USART_AUTOCR_TRIGSEL_Pos)
#define USART_AUTOCR_TRIGSEL_3              (0x0008UL << USART_AUTOCR_TRIGSEL_Pos)
#define USART_HWCFGR2_CFG1_Pos              (0UL)
#define USART_HWCFGR2_CFG1_Msk              (0xFUL << USART_HWCFGR2_CFG1_Pos)
#define USART_HWCFGR2_CFG1                  USART_HWCFGR2_CFG1_Msk
#define USART_HWCFGR2_CFG2_Pos              (4UL)
#define USART_HWCFGR2_CFG2_Msk              (0xFUL << USART_HWCFGR2_CFG2_Pos)
#define USART_HWCFGR2_CFG2                  USART_HWCFGR2_CFG2_Msk
#define USART_HWCFGR1_CFG1_Pos              (0UL)
#define USART_HWCFGR1_CFG1_Msk              (0xFUL << USART_HWCFGR1_CFG1_Pos)
#define USART_HWCFGR1_CFG1                  USART_HWCFGR1_CFG1_Msk
#define USART_HWCFGR1_CFG2_Pos              (4UL)
#define USART_HWCFGR1_CFG2_Msk              (0xFUL << USART_HWCFGR1_CFG2_Pos)
#define USART_HWCFGR1_CFG2                  USART_HWCFGR1_CFG2_Msk
#define USART_HWCFGR1_CFG3_Pos              (8UL)
#define USART_HWCFGR1_CFG3_Msk              (0xFUL << USART_HWCFGR1_CFG3_Pos)
#define USART_HWCFGR1_CFG3                  USART_HWCFGR1_CFG3_Msk
#define USART_HWCFGR1_CFG4_Pos              (12UL)
#define USART_HWCFGR1_CFG4_Msk              (0xFUL << USART_HWCFGR1_CFG4_Pos)
#define USART_HWCFGR1_CFG4                  USART_HWCFGR1_CFG4_Msk
#define USART_HWCFGR1_CFG5_Pos              (16UL)
#define USART_HWCFGR1_CFG5_Msk              (0xFUL << USART_HWCFGR1_CFG5_Pos)
#define USART_HWCFGR1_CFG5                  USART_HWCFGR1_CFG5_Msk
#define USART_HWCFGR1_CFG6_Pos              (20UL)
#define USART_HWCFGR1_CFG6_Msk              (0xFUL << USART_HWCFGR1_CFG6_Pos)
#define USART_HWCFGR1_CFG6                  USART_HWCFGR1_CFG6_Msk
#define USART_HWCFGR1_CFG7_Pos              (24UL)
#define USART_HWCFGR1_CFG7_Msk              (0xFUL << USART_HWCFGR1_CFG7_Pos)
#define USART_HWCFGR1_CFG7                  USART_HWCFGR1_CFG7_Msk
#define USART_HWCFGR1_CFG8_Pos              (28UL)
#define USART_HWCFGR1_CFG8_Msk              (0xFUL << USART_HWCFGR1_CFG8_Pos)
#define USART_HWCFGR1_CFG8                  USART_HWCFGR1_CFG8_Msk
#define USART_VERR_MINREV_Pos               (0UL)
#define USART_VERR_MINREV_Msk               (0xFUL << USART_VERR_MINREV_Pos)
#define USART_VERR_MINREV                   USART_VERR_MINREV_Msk
#define USART_VERR_MAJREV_Pos               (4UL)
#define USART_VERR_MAJREV_Msk               (0xFUL << USART_VERR_MAJREV_Pos)
#define USART_VERR_MAJREV                   USART_VERR_MAJREV_Msk
#define USART_IPIDR_ID_Pos                  (0UL)
#define USART_IPIDR_ID_Msk                  (0xFFFFFFFFUL << USART_IPIDR_ID_Pos)
#define USART_IPIDR_ID                      USART_IPIDR_ID_Msk
#define USART_SIDR_ID_Pos                   (0UL)
#define USART_SIDR_ID_Msk                   (0xFFFFFFFFUL << USART_SIDR_ID_Pos)
#define USART_SIDR_ID                       USART_SIDR_ID_Msk
