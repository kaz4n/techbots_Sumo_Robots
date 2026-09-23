// Retains exact numeric STM32U585 timer masks from the installed header.
// Source is P2_motor_native_raw/clock.json binding_bits, SHA256 8b66d5b9.
// Contract tests flip each guarded mode bit independently of production code.
#pragma once
#define TIM_CR1_CEN_Pos                     (0UL)
#define TIM_CR1_CEN_Msk                     (0x1UL << TIM_CR1_CEN_Pos)
#define TIM_CR1_CEN                         TIM_CR1_CEN_Msk
#define TIM_CR1_UDIS_Pos                    (1UL)
#define TIM_CR1_UDIS_Msk                    (0x1UL << TIM_CR1_UDIS_Pos)
#define TIM_CR1_UDIS                        TIM_CR1_UDIS_Msk
#define TIM_CR1_URS_Pos                     (2UL)
#define TIM_CR1_URS_Msk                     (0x1UL << TIM_CR1_URS_Pos)
#define TIM_CR1_URS                         TIM_CR1_URS_Msk
#define TIM_CR1_OPM_Pos                     (3UL)
#define TIM_CR1_OPM_Msk                     (0x1UL << TIM_CR1_OPM_Pos)
#define TIM_CR1_OPM                         TIM_CR1_OPM_Msk
#define TIM_CR1_DIR_Pos                     (4UL)
#define TIM_CR1_DIR_Msk                     (0x1UL << TIM_CR1_DIR_Pos)
#define TIM_CR1_DIR                         TIM_CR1_DIR_Msk
#define TIM_CR1_CMS_Pos                     (5UL)
#define TIM_CR1_CMS_Msk                     (0x3UL << TIM_CR1_CMS_Pos)
#define TIM_CR1_CMS                         TIM_CR1_CMS_Msk
#define TIM_CR1_CMS_0                       (0x1UL << TIM_CR1_CMS_Pos)
#define TIM_CR1_CMS_1                       (0x2UL << TIM_CR1_CMS_Pos)
#define TIM_CR1_ARPE_Pos                    (7UL)
#define TIM_CR1_ARPE_Msk                    (0x1UL << TIM_CR1_ARPE_Pos)
#define TIM_CR1_ARPE                        TIM_CR1_ARPE_Msk
#define TIM_CR1_CKD_Pos                     (8UL)
#define TIM_CR1_CKD_Msk                     (0x3UL << TIM_CR1_CKD_Pos)
#define TIM_CR1_CKD                         TIM_CR1_CKD_Msk
#define TIM_CR1_CKD_0                       (0x1UL << TIM_CR1_CKD_Pos)
#define TIM_CR1_CKD_1                       (0x2UL << TIM_CR1_CKD_Pos)
#define TIM_CR1_UIFREMAP_Pos                (11UL)
#define TIM_CR1_UIFREMAP_Msk                (0x1UL << TIM_CR1_UIFREMAP_Pos)
#define TIM_CR1_UIFREMAP                    TIM_CR1_UIFREMAP_Msk
#define TIM_CR1_DITHEN_Pos                  (12UL)
#define TIM_CR1_DITHEN_Msk                  (0x1UL << TIM_CR1_DITHEN_Pos)
#define TIM_CR1_DITHEN                      TIM_CR1_DITHEN_Msk
#define TIM_CR2_CCPC_Pos                    (0UL)
#define TIM_CR2_CCPC_Msk                    (0x1UL << TIM_CR2_CCPC_Pos)
#define TIM_CR2_CCPC                        TIM_CR2_CCPC_Msk
#define TIM_CR2_CCUS_Pos                    (2UL)
#define TIM_CR2_CCUS_Msk                    (0x1UL << TIM_CR2_CCUS_Pos)
#define TIM_CR2_CCUS                        TIM_CR2_CCUS_Msk
#define TIM_CR2_CCDS_Pos                    (3UL)
#define TIM_CR2_CCDS_Msk                    (0x1UL << TIM_CR2_CCDS_Pos)
#define TIM_CR2_CCDS                        TIM_CR2_CCDS_Msk
#define TIM_CR2_MMS_Pos                     (4UL)
#define TIM_CR2_MMS_Msk                     (0x200007UL << TIM_CR2_MMS_Pos)
#define TIM_CR2_MMS                         TIM_CR2_MMS_Msk
#define TIM_CR2_MMS_0                       (0x000001UL << TIM_CR2_MMS_Pos)
#define TIM_CR2_MMS_1                       (0x000002UL << TIM_CR2_MMS_Pos)
#define TIM_CR2_MMS_2                       (0x000004UL << TIM_CR2_MMS_Pos)
#define TIM_CR2_MMS_3                       (0x200000UL << TIM_CR2_MMS_Pos)
#define TIM_CR2_TI1S_Pos                    (7UL)
#define TIM_CR2_TI1S_Msk                    (0x1UL << TIM_CR2_TI1S_Pos)
#define TIM_CR2_TI1S                        TIM_CR2_TI1S_Msk
#define TIM_CR2_OIS1_Pos                    (8UL)
#define TIM_CR2_OIS1_Msk                    (0x1UL << TIM_CR2_OIS1_Pos)
#define TIM_CR2_OIS1                        TIM_CR2_OIS1_Msk
#define TIM_CR2_OIS1N_Pos                   (9UL)
#define TIM_CR2_OIS1N_Msk                   (0x1UL << TIM_CR2_OIS1N_Pos)
#define TIM_CR2_OIS1N                       TIM_CR2_OIS1N_Msk
#define TIM_CR2_OIS2_Pos                    (10UL)
#define TIM_CR2_OIS2_Msk                    (0x1UL << TIM_CR2_OIS2_Pos)
#define TIM_CR2_OIS2                        TIM_CR2_OIS2_Msk
#define TIM_CR2_OIS2N_Pos                   (11UL)
#define TIM_CR2_OIS2N_Msk                   (0x1UL << TIM_CR2_OIS2N_Pos)
#define TIM_CR2_OIS2N                       TIM_CR2_OIS2N_Msk
#define TIM_CR2_OIS3_Pos                    (12UL)
#define TIM_CR2_OIS3_Msk                    (0x1UL << TIM_CR2_OIS3_Pos)
#define TIM_CR2_OIS3                        TIM_CR2_OIS3_Msk
#define TIM_CR2_OIS3N_Pos                   (13UL)
#define TIM_CR2_OIS3N_Msk                   (0x1UL << TIM_CR2_OIS3N_Pos)
#define TIM_CR2_OIS3N                       TIM_CR2_OIS3N_Msk
#define TIM_CR2_OIS4_Pos                    (14UL)
#define TIM_CR2_OIS4_Msk                    (0x1UL << TIM_CR2_OIS4_Pos)
#define TIM_CR2_OIS4                        TIM_CR2_OIS4_Msk
#define TIM_CR2_OIS4N_Pos                   (15UL)
#define TIM_CR2_OIS4N_Msk                   (0x1UL << TIM_CR2_OIS4N_Pos)
#define TIM_CR2_OIS4N                       TIM_CR2_OIS4N_Msk
#define TIM_CR2_OIS5_Pos                    (16UL)
#define TIM_CR2_OIS5_Msk                    (0x1UL << TIM_CR2_OIS5_Pos)
#define TIM_CR2_OIS5                        TIM_CR2_OIS5_Msk
#define TIM_CR2_OIS6_Pos                    (18UL)
#define TIM_CR2_OIS6_Msk                    (0x1UL << TIM_CR2_OIS6_Pos)
#define TIM_CR2_OIS6                        TIM_CR2_OIS6_Msk
#define TIM_CR2_MMS2_Pos                    (20UL)
#define TIM_CR2_MMS2_Msk                    (0xFUL << TIM_CR2_MMS2_Pos)
#define TIM_CR2_MMS2                        TIM_CR2_MMS2_Msk
#define TIM_CR2_MMS2_0                      (0x1UL << TIM_CR2_MMS2_Pos)
#define TIM_CR2_MMS2_1                      (0x2UL << TIM_CR2_MMS2_Pos)
#define TIM_CR2_MMS2_2                      (0x4UL << TIM_CR2_MMS2_Pos)
#define TIM_CR2_MMS2_3                      (0x8UL << TIM_CR2_MMS2_Pos)
#define TIM_SMCR_SMS_Pos                    (0UL)
#define TIM_SMCR_SMS_Msk                    (0x10007UL << TIM_SMCR_SMS_Pos)
#define TIM_SMCR_SMS                        TIM_SMCR_SMS_Msk
#define TIM_SMCR_SMS_0                      (0x00001UL << TIM_SMCR_SMS_Pos)
#define TIM_SMCR_SMS_1                      (0x00002UL << TIM_SMCR_SMS_Pos)
#define TIM_SMCR_SMS_2                      (0x00004UL << TIM_SMCR_SMS_Pos)
#define TIM_SMCR_SMS_3                      (0x10000UL << TIM_SMCR_SMS_Pos)
#define TIM_SMCR_OCCS_Pos                   (3UL)
#define TIM_SMCR_OCCS_Msk                   (0x1UL << TIM_SMCR_OCCS_Pos)
#define TIM_SMCR_OCCS                       TIM_SMCR_OCCS_Msk
#define TIM_SMCR_TS_Pos                     (4UL)
#define TIM_SMCR_TS_Msk                     (0x30007UL << TIM_SMCR_TS_Pos)
#define TIM_SMCR_TS                         TIM_SMCR_TS_Msk
#define TIM_SMCR_TS_0                       (0x00001UL << TIM_SMCR_TS_Pos)
#define TIM_SMCR_TS_1                       (0x00002UL << TIM_SMCR_TS_Pos)
#define TIM_SMCR_TS_2                       (0x00004UL << TIM_SMCR_TS_Pos)
#define TIM_SMCR_TS_3                       (0x10000UL << TIM_SMCR_TS_Pos)
#define TIM_SMCR_TS_4                       (0x20000UL << TIM_SMCR_TS_Pos)
#define TIM_SMCR_MSM_Pos                    (7UL)
#define TIM_SMCR_MSM_Msk                    (0x1UL << TIM_SMCR_MSM_Pos)
#define TIM_SMCR_MSM                        TIM_SMCR_MSM_Msk
#define TIM_SMCR_ETF_Pos                    (8UL)
#define TIM_SMCR_ETF_Msk                    (0xFUL << TIM_SMCR_ETF_Pos)
#define TIM_SMCR_ETF                        TIM_SMCR_ETF_Msk
#define TIM_SMCR_ETF_0                      (0x1UL << TIM_SMCR_ETF_Pos)
#define TIM_SMCR_ETF_1                      (0x2UL << TIM_SMCR_ETF_Pos)
#define TIM_SMCR_ETF_2                      (0x4UL << TIM_SMCR_ETF_Pos)
#define TIM_SMCR_ETF_3                      (0x8UL << TIM_SMCR_ETF_Pos)
#define TIM_SMCR_ETPS_Pos                   (12UL)
#define TIM_SMCR_ETPS_Msk                   (0x3UL << TIM_SMCR_ETPS_Pos)
#define TIM_SMCR_ETPS                       TIM_SMCR_ETPS_Msk
#define TIM_SMCR_ETPS_0                     (0x1UL << TIM_SMCR_ETPS_Pos)
#define TIM_SMCR_ETPS_1                     (0x2UL << TIM_SMCR_ETPS_Pos)
#define TIM_SMCR_ECE_Pos                    (14UL)
#define TIM_SMCR_ECE_Msk                    (0x1UL << TIM_SMCR_ECE_Pos)
#define TIM_SMCR_ECE                        TIM_SMCR_ECE_Msk
#define TIM_SMCR_ETP_Pos                    (15UL)
#define TIM_SMCR_ETP_Msk                    (0x1UL << TIM_SMCR_ETP_Pos)
#define TIM_SMCR_ETP                        TIM_SMCR_ETP_Msk
#define TIM_SMCR_SMSPE_Pos                  (24UL)
#define TIM_SMCR_SMSPE_Msk                  (0x1UL << TIM_SMCR_SMSPE_Pos)
#define TIM_SMCR_SMSPE                      TIM_SMCR_SMSPE_Msk
#define TIM_SMCR_SMSPS_Pos                  (25UL)
#define TIM_SMCR_SMSPS_Msk                  (0x1UL << TIM_SMCR_SMSPS_Pos)
#define TIM_SMCR_SMSPS                      TIM_SMCR_SMSPS_Msk
#define TIM_CCMR1_IC2F_1                    (0x2UL << TIM_CCMR1_IC2F_Pos)
#define TIM_CCMR1_IC2F_2                    (0x4UL << TIM_CCMR1_IC2F_Pos)
#define TIM_CCMR1_IC2F_3                    (0x8UL << TIM_CCMR1_IC2F_Pos)
#define TIM_CCMR2_CC3S_Pos                  (0UL)
#define TIM_CCMR2_CC3S_Msk                  (0x3UL << TIM_CCMR2_CC3S_Pos)
#define TIM_CCMR2_CC3S                      TIM_CCMR2_CC3S_Msk
#define TIM_CCMR2_CC3S_0                    (0x1UL << TIM_CCMR2_CC3S_Pos)
#define TIM_CCMR2_CC3S_1                    (0x2UL << TIM_CCMR2_CC3S_Pos)
#define TIM_CCMR2_OC3FE_Pos                 (2UL)
#define TIM_CCMR2_OC3FE_Msk                 (0x1UL << TIM_CCMR2_OC3FE_Pos)
#define TIM_CCMR2_OC3FE                     TIM_CCMR2_OC3FE_Msk
#define TIM_CCMR2_OC3PE_Pos                 (3UL)
#define TIM_CCMR2_OC3PE_Msk                 (0x1UL << TIM_CCMR2_OC3PE_Pos)
#define TIM_CCMR2_OC3PE                     TIM_CCMR2_OC3PE_Msk
#define TIM_CCMR2_OC3M_Pos                  (4UL)
#define TIM_CCMR2_OC3M_Msk                  (0x1007UL << TIM_CCMR2_OC3M_Pos)
#define TIM_CCMR2_OC3M                      TIM_CCMR2_OC3M_Msk
#define TIM_CCMR2_OC3M_0                    (0x0001UL << TIM_CCMR2_OC3M_Pos)
#define TIM_CCMR2_OC3M_1                    (0x0002UL << TIM_CCMR2_OC3M_Pos)
#define TIM_CCMR2_OC3M_2                    (0x0004UL << TIM_CCMR2_OC3M_Pos)
#define TIM_CCMR2_OC3M_3                    (0x1000UL << TIM_CCMR2_OC3M_Pos)
#define TIM_CCMR2_OC3CE_Pos                 (7UL)
#define TIM_CCMR2_OC3CE_Msk                 (0x1UL << TIM_CCMR2_OC3CE_Pos)
#define TIM_CCMR2_OC3CE                     TIM_CCMR2_OC3CE_Msk
#define TIM_CCMR2_CC4S_Pos                  (8UL)
#define TIM_CCMR2_CC4S_Msk                  (0x3UL << TIM_CCMR2_CC4S_Pos)
#define TIM_CCMR2_CC4S                      TIM_CCMR2_CC4S_Msk
#define TIM_CCMR2_CC4S_0                    (0x1UL << TIM_CCMR2_CC4S_Pos)
#define TIM_CCMR2_CC4S_1                    (0x2UL << TIM_CCMR2_CC4S_Pos)
#define TIM_CCMR2_OC4FE_Pos                 (10UL)
#define TIM_CCMR2_OC4FE_Msk                 (0x1UL << TIM_CCMR2_OC4FE_Pos)
#define TIM_CCMR2_OC4FE                     TIM_CCMR2_OC4FE_Msk
#define TIM_CCMR2_OC4PE_Pos                 (11UL)
#define TIM_CCMR2_OC4PE_Msk                 (0x1UL << TIM_CCMR2_OC4PE_Pos)
#define TIM_CCMR2_OC4PE                     TIM_CCMR2_OC4PE_Msk
#define TIM_CCMR2_OC4M_Pos                  (12UL)
#define TIM_CCMR2_OC4M_Msk                  (0x1007UL << TIM_CCMR2_OC4M_Pos)
#define TIM_CCMR2_OC4M                      TIM_CCMR2_OC4M_Msk
#define TIM_CCMR2_OC4M_0                    (0x0001UL << TIM_CCMR2_OC4M_Pos)
#define TIM_CCMR2_OC4M_1                    (0x0002UL << TIM_CCMR2_OC4M_Pos)
#define TIM_CCMR2_OC4M_2                    (0x0004UL << TIM_CCMR2_OC4M_Pos)
#define TIM_CCMR2_OC4M_3                    (0x1000UL << TIM_CCMR2_OC4M_Pos)
#define TIM_CCMR2_OC4CE_Pos                 (15UL)
#define TIM_CCMR2_OC4CE_Msk                 (0x1UL << TIM_CCMR2_OC4CE_Pos)
#define TIM_CCMR2_OC4CE                     TIM_CCMR2_OC4CE_Msk
#define TIM_CCMR2_IC3PSC_Pos                (2UL)
#define TIM_CCMR2_IC3PSC_Msk                (0x3UL << TIM_CCMR2_IC3PSC_Pos)
#define TIM_CCMR2_IC3PSC                    TIM_CCMR2_IC3PSC_Msk
#define TIM_CCMR2_IC3PSC_0                  (0x1UL << TIM_CCMR2_IC3PSC_Pos)
#define TIM_CCMR2_IC3PSC_1                  (0x2UL << TIM_CCMR2_IC3PSC_Pos)
#define TIM_CCER_CC2NE_Msk                  (0x1UL << TIM_CCER_CC2NE_Pos)
#define TIM_CCER_CC2NE                      TIM_CCER_CC2NE_Msk
#define TIM_CCER_CC2NP_Pos                  (7UL)
#define TIM_CCER_CC2NP_Msk                  (0x1UL << TIM_CCER_CC2NP_Pos)
#define TIM_CCER_CC2NP                      TIM_CCER_CC2NP_Msk
#define TIM_CCER_CC3E_Pos                   (8UL)
#define TIM_CCER_CC3E_Msk                   (0x1UL << TIM_CCER_CC3E_Pos)
#define TIM_CCER_CC3E                       TIM_CCER_CC3E_Msk
#define TIM_CCER_CC3P_Pos                   (9UL)
#define TIM_CCER_CC3P_Msk                   (0x1UL << TIM_CCER_CC3P_Pos)
#define TIM_CCER_CC3P                       TIM_CCER_CC3P_Msk
#define TIM_CCER_CC3NE_Pos                  (10UL)
#define TIM_CCER_CC3NE_Msk                  (0x1UL << TIM_CCER_CC3NE_Pos)
#define TIM_CCER_CC3NE                      TIM_CCER_CC3NE_Msk
#define TIM_CCER_CC3NP_Pos                  (11UL)
#define TIM_CCER_CC3NP_Msk                  (0x1UL << TIM_CCER_CC3NP_Pos)
#define TIM_CCER_CC3NP                      TIM_CCER_CC3NP_Msk
#define TIM_CCER_CC4E_Pos                   (12UL)
#define TIM_CCER_CC4E_Msk                   (0x1UL << TIM_CCER_CC4E_Pos)
#define TIM_CCER_CC4E                       TIM_CCER_CC4E_Msk
#define TIM_CCER_CC4P_Pos                   (13UL)
#define TIM_CCER_CC4P_Msk                   (0x1UL << TIM_CCER_CC4P_Pos)
#define TIM_CCER_CC4P                       TIM_CCER_CC4P_Msk
#define TIM_CCER_CC4NE_Pos                  (14UL)
#define TIM_CCER_CC4NE_Msk                  (0x1UL << TIM_CCER_CC4NE_Pos)
#define TIM_CCER_CC4NE                      TIM_CCER_CC4NE_Msk
#define TIM_CCER_CC4NP_Pos                  (15UL)
#define TIM_CCER_CC4NP_Msk                  (0x1UL << TIM_CCER_CC4NP_Pos)
#define TIM_CCER_CC4NP                      TIM_CCER_CC4NP_Msk
#define TIM_CCER_CC5E_Pos                   (16UL)
#define TIM_CCER_CC5E_Msk                   (0x1UL << TIM_CCER_CC5E_Pos)
#define TIM_CCER_CC5E                       TIM_CCER_CC5E_Msk
#define TIM_CCER_CC5P_Pos                   (17UL)
#define TIM_CCER_CC5P_Msk                   (0x1UL << TIM_CCER_CC5P_Pos)
#define TIM_CCER_CC5P                       TIM_CCER_CC5P_Msk
#define TIM_CCER_CC6E_Pos                   (20UL)
#define TIM_CCER_CC6E_Msk                   (0x1UL << TIM_CCER_CC6E_Pos)
#define TIM_CCER_CC6E                       TIM_CCER_CC6E_Msk
#define TIM_CCER_CC6P_Pos                   (21UL)
#define TIM_CCER_CC6P_Msk                   (0x1UL << TIM_CCER_CC6P_Pos)
#define TIM_CCER_CC6P                       TIM_CCER_CC6P_Msk
#define TIM_CNT_CNT_Pos                     (0UL)
#define TIM_CNT_CNT_Msk                     (0xFFFFFFFFUL << TIM_CNT_CNT_Pos)
#define TIM_CNT_CNT                         TIM_CNT_CNT_Msk
#define TIM_CNT_UIFCPY_Pos                  (31UL)
#define TIM_CNT_UIFCPY_Msk                  (0x1UL << TIM_CNT_UIFCPY_Pos)
#define TIM_CNT_UIFCPY                      TIM_CNT_UIFCPY_Msk
#define TIM_PSC_PSC_Pos                     (0UL)
#define TIM_PSC_PSC_Msk                     (0xFFFFUL << TIM_PSC_PSC_Pos)
#define TIM_PSC_PSC                         TIM_PSC_PSC_Msk
#define TIM_ARR_ARR_Pos                     (0UL)
#define TIM_ARR_ARR_Msk                     (0xFFFFFFFFUL << TIM_ARR_ARR_Pos)
#define TIM_ARR_ARR                         TIM_ARR_ARR_Msk
#define TIM_RCR_REP_Pos                     (0UL)
#define TIM_RCR_REP_Msk                     (0xFFFFUL << TIM_RCR_REP_Pos)
#define TIM_RCR_REP                         TIM_RCR_REP_Msk
#define TIM_CCR1_CCR1_Pos                   (0UL)
#define TIM_CCR1_CCR1_Msk                   (0xFFFFFFFFUL << TIM_CCR1_CCR1_Pos)
#define TIM_CCR1_CCR1                       TIM_CCR1_CCR1_Msk
#define TIM_CCR6_CCR6_Pos                   (0UL)
#define TIM_CCR6_CCR6_Msk                   (0xFFFFFUL << TIM_CCR6_CCR6_Pos)
#define TIM_CCR6_CCR6                       TIM_CCR6_CCR6_Msk
#define TIM_BDTR_DTG_Pos                    (0UL)
#define TIM_BDTR_DTG_Msk                    (0xFFUL << TIM_BDTR_DTG_Pos)
#define TIM_BDTR_DTG                        TIM_BDTR_DTG_Msk
#define TIM_BDTR_DTG_0                      (0x01UL << TIM_BDTR_DTG_Pos)
#define TIM_BDTR_DTG_1                      (0x02UL << TIM_BDTR_DTG_Pos)
#define TIM_BDTR_DTG_2                      (0x04UL << TIM_BDTR_DTG_Pos)
#define TIM_BDTR_DTG_3                      (0x08UL << TIM_BDTR_DTG_Pos)
#define TIM_BDTR_DTG_4                      (0x10UL << TIM_BDTR_DTG_Pos)
#define TIM_BDTR_DTG_5                      (0x20UL << TIM_BDTR_DTG_Pos)
#define TIM_BDTR_DTG_6                      (0x40UL << TIM_BDTR_DTG_Pos)
#define TIM_BDTR_DTG_7                      (0x80UL << TIM_BDTR_DTG_Pos)
#define TIM_BDTR_LOCK_Pos                   (8UL)
#define TIM_BDTR_LOCK_Msk                   (0x3UL << TIM_BDTR_LOCK_Pos)
#define TIM_BDTR_LOCK                       TIM_BDTR_LOCK_Msk
#define TIM_BDTR_LOCK_0                     (0x1UL << TIM_BDTR_LOCK_Pos)
#define TIM_BDTR_LOCK_1                     (0x2UL << TIM_BDTR_LOCK_Pos)
#define TIM_BDTR_OSSI_Pos                   (10UL)
#define TIM_BDTR_OSSI_Msk                   (0x1UL << TIM_BDTR_OSSI_Pos)
#define TIM_BDTR_OSSI                       TIM_BDTR_OSSI_Msk
#define TIM_BDTR_OSSR_Pos                   (11UL)
#define TIM_BDTR_OSSR_Msk                   (0x1UL << TIM_BDTR_OSSR_Pos)
#define TIM_BDTR_OSSR                       TIM_BDTR_OSSR_Msk
#define TIM_BDTR_BKE_Pos                    (12UL)
#define TIM_BDTR_BKE_Msk                    (0x1UL << TIM_BDTR_BKE_Pos)
#define TIM_BDTR_BKE                        TIM_BDTR_BKE_Msk
#define TIM_BDTR_BKP_Pos                    (13UL)
#define TIM_BDTR_BKP_Msk                    (0x1UL << TIM_BDTR_BKP_Pos)
#define TIM_BDTR_BKP                        TIM_BDTR_BKP_Msk
#define TIM_BDTR_AOE_Pos                    (14UL)
#define TIM_BDTR_AOE_Msk                    (0x1UL << TIM_BDTR_AOE_Pos)
#define TIM_BDTR_AOE                        TIM_BDTR_AOE_Msk
#define TIM_BDTR_MOE_Pos                    (15UL)
#define TIM_BDTR_MOE_Msk                    (0x1UL << TIM_BDTR_MOE_Pos)
#define TIM_BDTR_MOE                        TIM_BDTR_MOE_Msk
#define TIM_BDTR_BKF_Pos                    (16UL)
#define TIM_BDTR_BKF_Msk                    (0xFUL << TIM_BDTR_BKF_Pos)
#define TIM_BDTR_BKF                        TIM_BDTR_BKF_Msk
#define TIM_BDTR_BK2F_Pos                   (20UL)
#define TIM_BDTR_BK2F_Msk                   (0xFUL << TIM_BDTR_BK2F_Pos)
#define TIM_BDTR_BK2F                       TIM_BDTR_BK2F_Msk
#define TIM_BDTR_BK2E_Pos                   (24UL)
#define TIM_BDTR_BK2E_Msk                   (0x1UL << TIM_BDTR_BK2E_Pos)
#define TIM_BDTR_BK2E                       TIM_BDTR_BK2E_Msk
#define TIM_BDTR_BK2P_Pos                   (25UL)
#define TIM_BDTR_BK2P_Msk                   (0x1UL << TIM_BDTR_BK2P_Pos)
#define TIM_BDTR_BK2P                       TIM_BDTR_BK2P_Msk
#define TIM_BDTR_BKDSRM_Pos                 (26UL)
#define TIM_BDTR_BKDSRM_Msk                 (0x1UL << TIM_BDTR_BKDSRM_Pos)
#define TIM_BDTR_BKDSRM                     TIM_BDTR_BKDSRM_Msk
#define TIM_BDTR_BK2DSRM_Pos                (27UL)
#define TIM_BDTR_BK2DSRM_Msk                (0x1UL << TIM_BDTR_BK2DSRM_Pos)
#define TIM_BDTR_BK2DSRM                    TIM_BDTR_BK2DSRM_Msk
#define TIM_BDTR_BKBID_Pos                  (28UL)
#define TIM_BDTR_BKBID_Msk                  (0x1UL << TIM_BDTR_BKBID_Pos)
#define TIM_BDTR_BKBID                      TIM_BDTR_BKBID_Msk
#define TIM_BDTR_BK2BID_Pos                 (29UL)
#define TIM_BDTR_BK2BID_Msk                 (0x1UL << TIM_BDTR_BK2BID_Pos)
#define TIM_BDTR_BK2BID                     TIM_BDTR_BK2BID_Msk
#define TIM_DCR_DBA_Pos                     (0UL)
#define TIM_DCR_DBA_Msk                     (0x1FUL << TIM_DCR_DBA_Pos)
#define TIM_DCR_DBA                         TIM_DCR_DBA_Msk
