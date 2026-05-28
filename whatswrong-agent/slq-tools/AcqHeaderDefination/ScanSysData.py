import ctypes
from ctypes import *

class EXAM_LEVEL_INFO_TYPE(ctypes.Structure):
    _fields_ = [
        ('suite_id', ctypes.c_char * 8),
        ('suite_id_sparse', ctypes.c_char * 64),
        ('product_id', ctypes.c_char * 65),
        ('hospital_name', ctypes.c_char * 65),
        ('character_set', ctypes.c_char * 17),
        ('patient_id', ctypes.c_char * 65),
        ('patient_name', ctypes.c_char * 70),
        ('patient_birthdate', ctypes.c_char * 11),
        ('patient_history', ctypes.c_char * 129),
        ('patient_ideographic_name', ctypes.c_char * 129),
        ('patient_phonetic_name', ctypes.c_char * 129),
        ('patient_info_integrity', ctypes.c_uint32 * 4),
        ('patient_age', ctypes.c_int32),
        ('patient_age_notation', ctypes.c_int),
        ('patient_sex', ctypes.c_int),
        ('patient_weight_grams', ctypes.c_int32),
        ('patient_height_mm', ctypes.c_int32),
        ('patient_info_sparse', ctypes.c_int32),
        ('patient_ethnic_group', ctypes.c_char * 17),
        ('other_patient_ids', ctypes.c_char * 65),
        ('other_patient_id2', ctypes.c_char * 65),
        ('patient_comments', ctypes.c_char * 129),
        ('physician_of_records', ctypes.c_char * 70),
        ('protocal_name', ctypes.c_char * 65),
        ('performed_procedure_step_id', ctypes.c_char * 17),
        ('performed_procedure_start_time', ctypes.c_uint32),
        ('performed_procedure_step_description', ctypes.c_char * 65),
        ('requested_procedure_id', ctypes.c_char * 17),
        ('scheduled_procedure_step_id', ctypes.c_char * 17),
        ('scheduled_procedure_step_description', ctypes.c_char * 65),
        ('exam_number', ctypes.c_int32),
        ('exam_datetime', ctypes.c_int32),
        ('exam_datetime_mms', ctypes.c_int32),
        ('accession_number', ctypes.c_char * 17),
        ('ref_physician', ctypes.c_char * 70),
        ('performing_physician', ctypes.c_char * 70),
        ('diag_radiologist', ctypes.c_char * 70),
        ('operator_id', ctypes.c_char * 70),
        ('exam_description', ctypes.c_char * 65),
        ('exam_type', ctypes.c_char * 70),
        ('creator_system_id', ctypes.c_char * 65),
        ('study_uid', ctypes.c_char * 65),
        ('exam_format', ctypes.c_int),
        ('ex_spare_d', ctypes.c_double * 8),
        ('software_version', ctypes.c_char * 65),
        ('device_serial_number', ctypes.c_char * 65),
        ('station_name', ctypes.c_char * 17),
        ('ex_spare_c', ctypes.c_char * 1),
        ('hybrid_reference_study_id', ctypes.c_char * 17),
        ('ex_spare_c2', ctypes.c_char * 3),
        ('pregnancy_status', ctypes.c_int),
        ('ex_spare', ctypes.c_int32 * 21)
    ]

class SCAN_SERIES_TYPE(ctypes.c_int):
    SCAN_SERIES_UNDEFINED = 0
    AXIAL_SCAN_SERIES = 1
    SCOUT_SCAN_SERIES = 3
    TIMING_BOLUS_SCAN_SERIES = 5
    SERVICE_AXIAL_SCAN_SERIES = 8
    SERVICE_SCOUT_SCAN_SERIES = 9
    SMARTSTEP_SCAN_SERIES = 90
    CT_INTERVENTIONAL_SCAN = 91

    def __repr__(self):
        return f'SCAN_SERIES_TYPE({self.value})'
    
class PATIENT_POSITION_TYPE(ctypes.c_int):
    PATIENT_POS_UNDEFINED = 0,
    PATIENT_POS_SUPINE = 1,
    PATIENT_POS_PRONE = 2,
    PATIENT_POS_DECUBITUS_LEFT = 4,
    PATIENT_POS_DECUBITUS_RIGHT = 8

    def __repr__(self):
        return f'PATIENT_POSITION_TYPE({self.value})'
    
class PATIENT_ENTRY_TYPE(ctypes.c_int):
    PATIENT_ENTRY_UNDEFINED = 0,
    PATIENT_ENTRY_HEAD_FIRST = 1,
    PATIENT_ENTRY_FEET_FIRST = 2

    def __repr__(self):
        return f'PATIENT_ENTRY_TYPE({self.value})'

class AUTO_INJECTION_MODE_TYPE(ctypes.c_int):
    AUTO_INJECTION_OFF = 0,
    AUTO_INJECTION_ON = 1

    def __repr__(self):
        return f'AUTO_INJECTION_MODE_TYPE({self.value})'
    
class CARDIAC_EARLY_BEAT_AVOIDANCE_MODE_TYPE(ctypes.c_int):
    EARLY_BEAT_AVOIDANCE_OFF = 0,
    EARLY_BEAT_AVOIDANCE_ON = 1

    def __repr__(self):
        return f'CARDIAC_EARLY_BEAT_AVOIDANCE_MODE_TYPE({self.value})'

class CARDIAC_EARLY_BEAT_AVOIDANCE_PARAMS_TYPE(ctypes.Structure):
    _fields_ = [
        ('cardiac_eba_mode', CARDIAC_EARLY_BEAT_AVOIDANCE_MODE_TYPE),
        ('eba_request_max', ctypes.c_int32)
    ]

class YES_NO_TYPE(ctypes.c_uint32):
    YES_NO_UNINIT = 0xFFFFFFFF
    NO = 0
    YES = 1

    def __repr__(self):
        return f'YES_NO_TYPE({self.value:#010x})'

class SERIES_LEVEL_INFO_TYPE(ctypes.Structure):
    _fields_ = [
        ('series_number', ctypes.c_int32),
        ('series_datetime', ctypes.c_int32),
        ('series_datetime_mms', ctypes.c_int32),
        ('series_type', SCAN_SERIES_TYPE),
        ('patient_position', PATIENT_POSITION_TYPE),
        ('patient_entry', PATIENT_ENTRY_TYPE),
        ('auto_injection_mode', AUTO_INJECTION_MODE_TYPE),
        ('inj_spare', ctypes.c_int32),
        ('horizontal_landmark_mm', ctypes.c_double),
        ('series_desc', ctypes.c_char * 65),
        ('anatomical_ref', ctypes.c_char * 8),
        ('series_uid', ctypes.c_char * 65),
        ('landmark_uid', ctypes.c_char * 65),
        ('anatomy_region_codeValue', ctypes.c_char * 17),
        ('anatomy_region_codeScheme', ctypes.c_char * 17),
        ('anatomy_region_codeMeaning', ctypes.c_char * 17),
        ('num_of_sch_proc_steps', ctypes.c_int32),
        ('num_supported_contrast', ctypes.c_int32),
        ('se_spare_d', ctypes.c_double * 8),
        ('cardiac_eda_params', CARDIAC_EARLY_BEAT_AVOIDANCE_PARAMS_TYPE),
        ('last_series_in_exam', YES_NO_TYPE),
        ('acquisition_parent_uid', ctypes.c_char * 68),
        ('se_spare', ctypes.c_int32 * 46),
    ]

class SCAN_MODE_TYPE(ctypes.c_int):
    SCAN_MODE_NOT_SCANNING = 0,
    SCAN_MODE_AXIAL = 1,
    SCAN_MODE_DYNAMIC = 2,
    SCAN_MODE_SCOUT = 4,
    SCAN_MODE_AXIAL_XRAYON = 8,
    SCAN_MODE_AXIAL_XRAYOFF = 16,
    SCAN_MODE_RESERVED1 = 32,
    SCAN_MODE_STATIC_XRAYOFF = 64,
    SCAN_MODE_TUBE_HEAT = 128,
    SCAN_MODE_DAS = 256,
    SCAN_MODE_TUBE_CAL = 512,
    SCAN_MODE_BIOPSY = 1024,
    SCAN_MODE_CINE = 2048,
    SCAN_MODE_HELICAL = 4096,
    SCAN_MODE_ROTGENCAL = 8192,
    SCAN_MODE_CINE_PULSE = 16384,
    SCAN_MODE_RESERVED2 = 32768,
    SCAN_MODE_IV_ONESHOT = 65536,
    SCAN_MODE_IV_3D_GUIDANCE = 131072

    def __repr__(self):
        return f'SCAN_MODE_TYPE({self.value})'
    
class APPLICATION_MODE_TYPE(ctypes.c_int):
    PATIENT_SCANNING_MODE = 0,
    SERVICE_SCANNING_MODE = 1

    def __repr__(self):
        return f'APPLICATION_MODE_TYPE({self.value})'

class TUBE_COOLING_MODE_TYPE(ctypes.c_int):
    INTER_SCAN_TUBE_COOLING = 0,
    PRE_SCAN_TUBE_COOLING = 1
    
    def __repr__(self):
        return f'TUBE_COOLING_MODE_TYPE({self.value})'
    
class ROTATION_TYPE(ctypes.c_int):
    ROTATION_UNDEFINED = 0,
    HALF_SCAN = 1,
    NORMAL_SCAN = 2,
    OVER_SCAN = 4,
    STATIONARY = 8

    def __repr__(self):
        return f'ROTATION_TYPE({self.value})'
    
class TRACKING_MODE_TYPE(ctypes.c_int):
    TRACKING_MODE_OFF = 0,
    TRACKING_MODE_NORMAL = 1,
    TRACKING_MODE_MEASURE = 2,
    TRACKING_MODE_AIRCAL = 3,
    TRACKING_MODE_FIXED_COLL = 4,
    TRACKING_MODE_FIXED_COLL_AIRCAL = 5,
    TRACKING_MODE_WILD = 6

    def __repr__(self):
        return f'TRACKING_MODE_TYPE({self.value})'
    
class SCAN_PRESCRIPTION_TYPE(ctypes.c_int):
    SCAN_PRESCRIPTION_TYPE_UNKNOWN = 0,
    REGULAR_PATIENT_SCAN = 1,
    SMARTPREP_BASELINE_SCAN = 2,
    SMARTPREP_MONITORING_SCAN = 3,
    CALIBRATION_SCAN = 4,
    SERVICE_SCAN = 5

    def __repr__(self):
        return f'SCAN_PRESCRIPTION_TYPE({self.value})'
    

class FOCAL_SPOT_TYPE(ctypes.c_int):
    FOCAL_SPOT_WILD = 0,
    FOCAL_SPOT_SMALL = 1,
    FOCAL_SPOT_LARGE = 2,
    FOCAL_SPOT_MEDIUM = 3,
    FOCAL_SPOT_XLARGE = 4,
    FOCAL_SPOT_XSMALL = 5

    def __repr__(self):
        return f'FOCAL_SPOT_TYPE({self.value})'

class KV_MODULATION_TYPE(ctypes.c_int):
    KV_MODULATION_NONE = 0,
    KV_MODULATION_DUAL = 1,
    KV_MODULATION_FAST = 2,
    KV_MODULATION_FAST_DWELL = 3,
    KV_MODULATION_WILD = 4

    def __repr__(self):
        return f'KV_MODULATION_TYPE({self.value})'
    
class KV_MODULATION_PARAMS_TYPE(ctypes.Structure):
    _fields_ = [
        ('mode', KV_MODULATION_TYPE),
        ('second_kV', ctypes.c_int32),
        ('second_mA', ctypes.c_int32),
        ('options', ctypes.c_int32),
        ('first_exposure_sec', ctypes.c_double),
        ('time_between_exp_sec', ctypes.c_double),
        ('second_exposure_sec', ctypes.c_double),
        ('base_dose', ctypes.c_double),
        ('spare_d2', ctypes.c_double),
        ('trig_duty_cycle_percent', ctypes.c_uint32),
        ('kv_duty_cycle_percent', ctypes.c_uint32),
        ('kv_skew_usec', ctypes.c_int32),
        ('effective_kv_high', ctypes.c_float),
        ('effective_kv_low', ctypes.c_float),
        ('effective_ma', ctypes.c_uint32),
        ('dwell_triggers_kv_high', ctypes.c_uint32),
        ('dwell_triggers_kv_low', ctypes.c_uint32),
        ('spares', ctypes.c_uint32 * 2),
    ]

class AUTO_MA_TYPE(ctypes.c_int):
    MANUAL_MA_MODE = 0,
    AUTO_MA_MODE = 1,
    SMART_MA_MODE = 2,
    ECG_MODULATED_MA_MODE = 3,
    ODM_MA_MODE = 4

    def __repr__(self):
        return f'AUTO_MA_TYPE({self.value})'

class SMART_SCAN_PHASE_TYPE(ctypes.c_int):
    SMART_SCAN_START_MAX = 0,
    SMART_SCAN_START_MIN = 1

    def __repr__(self):
        return f'SMART_SCAN_PHASE_TYPE({self.value})'
    
class DOSE_MODE_TYPE(ctypes.c_int):
    DOSE_MODE_NORMAL = 0,
    DOSE_MODE_LOW = 1

    def __repr__(self):
        return f'DOSE_MODE_TYPE({self.value})'
    
class Z_CHAN_CONFIG_TYPE(ctypes.c_int):
    Z_CHAN_NORMAL = 0,
    Z_CHAN_DUAL = 1

    def __repr__(self):
        return f'Z_CHAN_CONFIG_TYPE({self.value})'

class MACRO_ROW_WIDTH_TYPE(ctypes.c_int):
    MACRO_ROW_WIDTH_CLOSED = 0,
    MACRO_ROW_WIDTH_1_25MM = 1,
    MACRO_ROW_WIDTH_2_50MM = 2,
    MACRO_ROW_WIDTH_3_75MM = 3,
    MACRO_ROW_WIDTH_5_00MM = 4,
    MACRO_ROW_WIDTH_6_25MM = 5,
    MACRO_ROW_WIDTH_7_50MM = 6,
    MACRO_ROW_WIDTH_8_75MM = 7,
    MACRO_ROW_WIDTH_10_00MM = 8,
    MACRO_ROW_WIDTH_0_625MM = 9,
    MACRO_ROW_WIDTH_1_875MM = 10,
    MACRO_ROW_WIDTH_0_417MM = 11

    def __repr__(self):
        return f'MACRO_ROW_WIDTH_TYPE({self.value})'
    
class NUM_MACRO_ROWS_TYPE(ctypes.c_int):
    MACRO_ROWS_UNDEFINED = 0,
    MACRO_ROWS_1 = 1,
    MACRO_ROWS_2 = 2,
    MACRO_ROWS_4 = 4,
    MACRO_ROWS_5 = 5,
    MACRO_ROWS_6 = 6,
    MACRO_ROWS_7 = 7,
    MACRO_ROWS_8 = 8,
    MACRO_ROWS_9 = 9,
    MACRO_ROWS_10 = 10,
    MACRO_ROWS_12 = 12,
    MACRO_ROWS_14 = 14,
    MACRO_ROWS_16 = 16,
    MACRO_ROWS_24 = 24,
    MACRO_ROWS_32 = 32,
    MACRO_ROWS_40 = 40,
    MACRO_ROWS_48 = 48,
    MACRO_ROWS_64 = 64,
    MACRO_ROWS_80 = 80,
    MACRO_ROWS_96 = 96,
    MACRO_ROWS_128 = 128,
    MACRO_ROWS_144 = 144,
    MACRO_ROWS_160 = 160,
    MACRO_ROWS_192 = 192,
    MACRO_ROWS_224 = 224,
    MACRO_ROWS_256 = 256,
    MACRO_ROWS_240 = 240,
    MACRO_ROWS_288 = 288,
    MACRO_ROWS_336 = 336,
    MACRO_ROWS_384 = 384

    def __repr__(self):
        return f'NUM_MACRO_ROWS_TYPE({self.value})'
    
class FILTER_TYPE(ctypes.c_int):
    FILTER_CLOSED = 0,
    FILTER_AIR = 1,
    FILTER_BODY = 2,
    FILTER_HEAD = 3,
    FILTER_MEDIUM = 4,
    FILTER_FLAT = 5,
    FILTER_LARGE_COPPER = 6,
    FILTER_LARGE_SMART = 7,
    FILTER_UNIFORM_THICKNESS = 8

    def __repr__(self):
        return f'FILTER_TYPE({self.value})'
    
class SCAN_FOV_TYPE(ctypes.c_int):
    SFOV_UNDEFINED = 0,
    SFOV_PED_HEAD = 1,
    SFOV_ADULT_HEAD = 2,
    SFOV_SMALL = 4,
    SFOV_MEDIUM_OBSOLETE = 8,
    SFOV_LARGE = 16,
    SFOV_NOFILTER = 32,
    SFOV_SHOULDER = 64,
    SFOV_SMALL_HEAD = 2049,
    SFOV_SMALL_BODY = 256,
    SFOV_RESERVED1 = 512,
    SFOV_RESERVED2 = 1024,
    SFOV_PED_BODY = 2048,
    SFOV_CARDIAC_SMALL = 2050,
    SFOV_CARDIAC_MEDIUM = 2051,
    SFOV_CARDIAC_LARGE = 2052,
    SFOV_LARGE_COPPER = 2053,
    SFOV_UNIFORM_THICKNESS = 2054,
    SFOV_WILD = 128

    def __repr__(self):
        return f'SCAN_FOV_TYPE({self.value})'
    
class PLANE_TYPE(ctypes.c_int32):
    PLANE_UNDEFINED = 0,
    SCOUT_PLANE = 1,
    AXIAL_PLANE = 2

    def __repr__(self):
        return f'PLANE_TYPE({self.value})'

class CONTRAST_TYPE(ctypes.c_int):
    CONTRAST_NONE = 0,
    CONTRAST_ORAL = 1,
    CONTRAST_IV = 2,
    CONTRAST_ORAL_IV = 3

    def __repr__(self):
        return f'CONTRAST_TYPE({self.value})'
    
class CONTRAST_INFO_TYPE(ctypes.Structure):
    _fields_ = [
        ('contrast_type', CONTRAST_TYPE),
        ('contrast_oral', ctypes.c_char * 24),
        ('contrastIV', ctypes.c_char * 24)
    ]

class WAVEFORM_TYPE(ctypes.c_int):
    WAVEFORM_UNKNOWN = 0,
    EKG_WAVEFORM = 1,
    RESPIRATION_WAVEFORM = 2,
    MODULATED_MA_WAVEFORM = 3

    def __repr__(self):
        return f'WAVEFORM_TYPE({self.value})'
    
class WAVEFORM_INFO_TYPE(ctypes.Structure):
    _fields_ = [
        ('waveform_available', YES_NO_TYPE),
        ('waveform_saved', YES_NO_TYPE),
        ('waveform_type', WAVEFORM_TYPE)
    ]

class EKG_GATING_TYPE(ctypes.c_int):
    EKG_GATING_UNKNOWN = 0,
    EKG_GATING_DEFAULT = 1

    def __repr__(self):
        return f'EKG_GATING_TYPE({self.value})'
    
class GATING_TYPE(ctypes.c_int):
    GATING_TYPE_NONE = 0,
    GATING_TYPE_CARDIAC = 1,
    GATING_TYPE_PULMONARY = 2

    def __repr__(self):
        return f'GATING_TYPE({self.value})'

class RATE_DETECT_TYPE(ctypes.c_int):
    RATE_DETECT_MANUAL = 0,
    RATE_DETECT_AUTO_ALG_1 = 1

    def __repr__(self):
        return f'RATE_DETECT_TYPE({self.value})'
    
class GATING_RX_INFO_TYPE(ctypes.Structure):
    _fields_ = [
        ('gatingType', GATING_TYPE),
        ('triggerDelay', ctypes.c_int32),
        ('triggerDelayOffset_ms', ctypes.c_int32),
        ('minGatingRate', ctypes.c_int32),
        ('maxGatingRate', ctypes.c_int32),
        ('monitoringType', GATING_TYPE),
        ('minMonitorRate', ctypes.c_int32),
        ('maxMonitorRate', ctypes.c_int32),
        ('systemOptimizedMonitorRate', ctypes.c_int32),
        ('monitorRateDetect', RATE_DETECT_TYPE),
        ('monitorRateAtConfirm', ctypes.c_int32),
        ('avgMonitorRatePriorToConfirm', ctypes.c_float),
        ('minMonitorRatePriorToConfirm', ctypes.c_int32),
        ('maxMonitorRatePriorToConfirm', ctypes.c_int32),
        ('stddevMonitorRatePriorToConfirm', ctypes.c_float),
        ('numMonitorRateSamplesPriorToConfirm', ctypes.c_int32),
        ('gatingDeviceName', ctypes.c_char * 32),
        ('monitoringDeviceName', ctypes.c_char * 32)
    ]

class ROTOR_SPEED_TYPE(c_int):
    ROTOR_SPEED_UNDEFINED = 0,
    ROTOR_SPEED_OFF = 1,
    ROTOR_SPEED_LOW = 2,
    ROTOR_SPEED_MEDIUM = 3,
    ROTOR_SPEED_HIGH = 4

    def __repr__(self):
        return f'ROTOR_SPEED_TYPE({self.value})'

class FW_RX_OVERRIDE_TYPE(ctypes.Structure):
    _fields_ = [
        ('rx_overriedes', ctypes.c_uint32),
        ('filament_i', ctypes.c_double),
        ('anode_dac', ctypes.c_int32),
        ('cathode_dac', c_int32),
        ('rotorspeed', ROTOR_SPEED_TYPE),
        ('xray_delay_sec', c_double),
        ('xray_duration_sec', c_double),
        ('interventional_overrides', c_uint32),
        ('options', c_uint32),
        ('trigger_delay', c_int32),
        ('trigger_delay_offset', c_int32),
        ('trigger_margin_percent', c_int32),
        ('ramp_up_time_msec', c_int32),
        ('p1', c_int32 * 17),
        ('inputOffsetVoltage', c_double),
        ('p2', c_int32 * 50)
    ]

class SMART_CATHODE_MODE_TYPE(c_int):
    SC_DEFLECT_BIAS_OFF = 0,
    SC_BIAS_MODE = 1,
    SC_STATIC_DEFLECT = 2,
    SC_DYNAMIC_DEFLECT = 3

    def __repr__(self):
        return f'SMART_CATHODE_MODE_TYPE({self.value})'

class SMART_CATHODE_PARAMETERS_TYPE(Structure):
    _fields_ = [
        ('smart_cathode_mode', SMART_CATHODE_MODE_TYPE),
        ('mode_options', c_uint32),
        ('cathode_deflection_points', c_uint32)
    ]

class HELICAL_SHUTTLE_PARAMS_TYPE(Structure):
    _fields_ = [
        ('helical_shuttle_flag', YES_NO_TYPE), 
        ('p1', c_uint32 * 15)
    ]

class SCAN_SEGMENT_INFO_TYPE(Structure):
    _fields_ = [
        ('p1', c_double * 7),
        ('p2', c_int32 * 6)
    ]

class SHUTTER_PARAMS_TYPE(Structure):
    _fields_ = [
        ('p1', c_uint32 * 2),
        ('p2', c_float),
        ('p3', c_uint32 * 2),
        ('p4', c_float),
        ('p5', c_uint32),
        ('p6', c_float * 2),
        ('p7', c_uint32)
    ]

class CTDI_INTERPOLATION_PARAMS_TYPE(Structure):
    _fields_ = [
        ('p1', c_double * 4)
    ]

class ODM_PARAM_TYPE(Structure):
    _fields_ = [
        ('p1', c_double * 5)
    ]

class ODM_CLUSTER_INFO(Structure):
    _fields_ = [
        ('p1', c_double * 3),
        ('p2', ODM_PARAM_TYPE * 2)
    ]

class CARDIAC_PHASE_TYPE(Structure):
    _fields_ = [
        ('p1', c_float * 4),
        ('p2', c_uint32 * 3)
    ]

class CARDIAC_AAM_PARAMS_TYPE(Structure):
    _fields_ = [
        ('p1', c_uint32 * 3),
        ('p2', c_float),
        ('p3', c_uint32),
        ('p4', c_int32 * 2)
    ]

class CARDIAC_MULTIPHASE_PARAM_TYPE(Structure):
    _fields_ = [
        ('p1', c_uint32 * 6),
        ('p2', CARDIAC_PHASE_TYPE * 3),
        ('p3', c_uint32 * 7),
        ('p4', c_float * 2),
        ('p5', c_uint32 * 2),
        ('p6', c_float * 3),
        ('p7', CARDIAC_AAM_PARAMS_TYPE)
    ]

class SCAN_LEVEL_INFO_TYPE(ctypes.Structure):
    _fields_ = [
        ('scan_mode', SCAN_MODE_TYPE),
        ('application_mode', APPLICATION_MODE_TYPE),
        ('prescribed_scan_type', SCAN_PRESCRIPTION_TYPE),
        ('tube_cooling_mode', TUBE_COOLING_MODE_TYPE),
        ('rotation_type', ROTATION_TYPE),
        ('z_axis_tracking', TRACKING_MODE_TYPE),
        ('scan_time_sec', ctypes.c_double),
        ('kvolt', ctypes.c_int32),
        ('mamp', ctypes.c_int32),
        ('spot_size', FOCAL_SPOT_TYPE),
        ('dkv_padding', ctypes.c_int32),
        ('kv_modulation_params', KV_MODULATION_PARAMS_TYPE),
        ('dual_kv_spare', ctypes.c_int32 * 7),
        ('smart_scan_flag', AUTO_MA_TYPE),
        ('smart_scan_minimum_ma', ctypes.c_int32),
        ('smart_scan_modulation_percent', ctypes.c_int32),
        ('smart_scan_phase', SMART_SCAN_PHASE_TYPE),
        ('smart_scan_mamp', ctypes.c_int32),
        ('acquisition_mode', ctypes.c_uint32),
        ('dose_mode', DOSE_MODE_TYPE),
        ('z_chan_config_type', Z_CHAN_CONFIG_TYPE),
        ('det_macro_width_iso', MACRO_ROW_WIDTH_TYPE),
        ('number_detector_macro_rows', NUM_MACRO_ROWS_TYPE),
        ('gantry_filter', FILTER_TYPE),
        ('scan_pitch_ratio', ctypes.c_char * 8),
        ('start_ras', ctypes.c_char),
        ('end_ras', ctypes.c_char),
        ('number_of_pretriggers', ctypes.c_int32),
        ('trigger_frequency_hz', ctypes.c_double),
        ('table_start_mm', ctypes.c_double),
        ('actual_table_start_mm', ctypes.c_double),
        ('table_end_mm', ctypes.c_double),
        ('actual_table_end_mm', ctypes.c_double),
        ('table_speed_mm_sec', ctypes.c_double),
        ('gantry_period_sec_rev', ctypes.c_double),
        ('views_per_rotation', ctypes.c_double),
        ('gantry_tilt_deg', ctypes.c_double),
        ('actual_gantry_tilt_deg', ctypes.c_double),
        ('azimuth_deg', ctypes.c_double),
        ('exclude_angle_width_deg', ctypes.c_double),
        ('symm_180', YES_NO_TYPE),
        ('das_gain', ctypes.c_int32),
        ('z_chan_das_gain', ctypes.c_int32),
        ('das_spare', ctypes.c_int32),
        ('scan_fov_type', SCAN_FOV_TYPE),
        ('scan_fov_mm', ctypes.c_double),
        ('scan_plane', PLANE_TYPE),
        ('contrast_info', CONTRAST_INFO_TYPE),
        ('rx_series_number', c_int32),
        ('rx_image_number', c_int32),
        ('rx_image_uid', c_char * 65),
        ('waveform_info', WAVEFORM_INFO_TYPE * 5),
        ('ekg_gating_type', EKG_GATING_TYPE),
        ('gating_rx', GATING_RX_INFO_TYPE),
        ('overrides', FW_RX_OVERRIDE_TYPE),
        ('smart_cathode_params', SMART_CATHODE_PARAMETERS_TYPE),
        ('helical_shuttle_params', HELICAL_SHUTTLE_PARAMS_TYPE),
        ('das_trigger_source', c_int32),
        ('das_fpggain', c_int32),
        ('das_output_source', c_int32),
        ('das_ad_input', c_int32),
        ('das_cal_mode', c_int32),
        ('group_id', c_uint32),
        ('group_scan_spacing_mm', c_double),
        ('gsi_scan_mode_key_label', c_char * 128),
        ('num_scan_segments', c_int32),
        ('segment_type', c_int32),
        ('scan_segment', SCAN_SEGMENT_INFO_TYPE * 5),
        ('offset_collection_mode_override', c_int32),
        ('offset_collection_mode', c_int32),
        ('gsi_annotation_ma', c_int32),
        ('arythmia_mgmt_spare', c_int32 * 8),
        ('shutter_params', SHUTTER_PARAMS_TYPE),
        ('dose_dlp_per_sec', c_double),
        ('ctdi_params', CTDI_INTERPOLATION_PARAMS_TYPE),
        ('num_of_odm_cluster', c_int32),
        ('odm_cluster_info', ODM_CLUSTER_INFO * 3),
        ('cardiac_multiphase', CARDIAC_MULTIPHASE_PARAM_TYPE),
        ('num_exposures', c_int32),
        ('irradiationEventId', c_char * 64),
        ('enable_elevation_check', YES_NO_TYPE), 
        ('elevation_position_mm', c_double),
        ('elevation_automove', YES_NO_TYPE),
        ('scout_type', c_int32),
        ('effective_mA', c_uint32),
        ('raw_data_collection_mode', c_int32),
        ('sc_spare', c_int32 * 18)
    ]

def calcStructureInfo(struct_type):
    print(f"Size of {struct_type.__name__}: {ctypes.sizeof(struct_type)} bytes")

if __name__ == '__main__':
    calcStructureInfo(SCAN_SERIES_TYPE)