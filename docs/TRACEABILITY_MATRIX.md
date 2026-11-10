# 🧭 Matice trasovatelnosti (Traceability Matrix)

* **Byznysové požadavky:** 19 User Stories (100 % pokryto v katalogu testů)
* **Celkem specifikovaných testů:** 48 (v [`docs/TEST_CASES.md`](TEST_CASES.md))
* **Pokryto automatizací:** 48 (100.0 %)
* **Chybějící scénáře:** 0
* **Testy s evidovaným defektem (XFAIL):** 9 (viz [`docs/JIRA_BUG_REPORTS.md`](JIRA_BUG_REPORTS.md))
* **Neshody v markerech:** 0

---

## 📋 Kompletní přehled testovacích případů

| Modul | User Story | Kód testu | Název testovacího případu | Stav v kódu | Markery | Implementace v kódu |
| :---: | :---: | :---: | :--- | :---: | :---: | :--- |
| **AUTH** | [`US-01`](požadavky_ust_podle_src.md) | `TC-01-AUTH` | AK-1, AK-7, AK-8 | 🟢 Pokryto | `auth`, `smoke` | [`test_register.py:27`](../tests/auth/test_register.py#L27) -> `test_tc01_auth_successful_registration_and_password_masking` |
| **AUTH** | [`US-01`](požadavky_ust_podle_src.md) | `TC-02-AUTH` | AK-3, AK-6 | 🟢 Pokryto | `auth`, `regression` | [`test_register.py:141`](../tests/auth/test_register.py#L141) -> `test_tc02_auth_registration_duplicate_email` |
| **AUTH** | [`US-01`](požadavky_ust_podle_src.md) | `TC-03-AUTH` | AK-5, AK-6 | 🟢 Pokryto | `auth`, `regression`, `parametrize` | [`test_register.py:81`](../tests/auth/test_register.py#L81) -> `test_tc03_auth_registration_password_mismatch_and_empty_confirmation` |
| **AUTH** | [`US-01`](požadavky_ust_podle_src.md) | `TC-04-AUTH` | AK-2, AK-3, AK-5, AK-6 | 🟢 Pokryto | `auth`, `regression` | [`test_register.py:56`](../tests/auth/test_register.py#L56) -> `test_tc04_auth_registration_required_fields_validation` |
| **AUTH** | [`US-01`](požadavky_ust_podle_src.md) | `TC-05-AUTH` | AK-4 | 🟢 Pokryto | `auth`, `regression` | [`test_register.py:186`](../tests/auth/test_register.py#L186) -> `test_tc05_auth_email_normalization_on_registration` |
| **AUTH** | [`US-02`](požadavky_ust_podle_src.md) | `TC-06-AUTH` | AK-1, AK-5, AK-6 | 🟢 Pokryto | `auth`, `smoke`, `parametrize` | [`test_login.py:41`](../tests/auth/test_login.py#L41) -> `test_tc06_auth_successful_login_variants` |
| **AUTH** | [`US-02`](požadavky_ust_podle_src.md) | `TC-07-AUTH` | AK-4 | 🟢 Pokryto | `auth`, `smoke`, `parametrize` | [`test_login.py:106`](../tests/auth/test_login.py#L106) -> `test_tc07_auth_invalid_and_incomplete_login_credentials` |
| **AUTH** | [`US-02`](požadavky_ust_podle_src.md) | `TC-08-AUTH` | AK-2 | 🟢 Pokryto | `auth`, `regression`, `parametrize` | [`test_login.py:137`](../tests/auth/test_login.py#L137) -> `test_tc08_auth_invalid_email_format_validation` |
| **AUTH** | [`US-02`](požadavky_ust_podle_src.md) | `TC-09-AUTH` | AK-3 | 🟢 Pokryto | `auth`, `smoke` | [`test_logout.py:33`](../tests/auth/test_logout.py#L33) -> `test_tc09_auth_session_persists_after_page_reload` |
| **AUTH** | [`US-02`](požadavky_ust_podle_src.md) | `TC-10-AUTH` | AK-7 | 🟢 Pokryto | `auth`, `regression` | [`test_login.py:265`](../tests/auth/test_login.py#L265) -> `test_tc10_auth_keyboard_navigation_tab_and_enter` |
| **AUTH** | [`US-03`](požadavky_ust_podle_src.md) | `TC-11-AUTH` | AK-1, AK-2, AK-3, AK-4 | 🟢 Pokryto | `auth`, `smoke` | [`test_logout.py:20`](../tests/auth/test_logout.py#L20) -> `test_tc11_auth_login_and_logout_lifecycle` |
| **AUTH** | [`US-04`](požadavky_ust_podle_src.md) | `TC-12-AUTH` | AK-1, AK-4 | 🟢 Pokryto | `auth`, `regression` | [`test_password_reset.py:24`](../tests/auth/test_password_reset.py#L24) -> `test_tc12_auth_forgot_password_request_submission` |
| **AUTH** | [`US-04`](požadavky_ust_podle_src.md) | `TC-13-AUTH` | AK-2, AK-3 | 🟢 Pokryto | `auth`, `regression` | [`test_password_reset.py:38`](../tests/auth/test_password_reset.py#L38) -> `test_tc13_auth_forgot_password_invalid_or_empty_email_validation` |
| **AUTH** | [`US-05`](požadavky_ust_podle_src.md) | `TC-14-AUTH` | AK-2, AK-4 | ⚠️ XFAIL ([BR-03](JIRA_BUG_REPORTS.md)) | `auth`, `regression`, `xfail` | [`test_password_reset.py:62`](../tests/auth/test_password_reset.py#L62) -> `test_tc14_auth_successful_password_reset_with_valid_token` |
| **AUTH** | [`US-05`](požadavky_ust_podle_src.md) | `TC-15-AUTH` | AK-1, AK-5 | 🟢 Pokryto | `auth`, `regression` | [`test_password_reset.py:82`](../tests/auth/test_password_reset.py#L82) -> `test_tc15_auth_password_reset_invalid_or_expired_token` |
| **AUTH** | [`US-05`](požadavky_ust_podle_src.md) | `TC-16-AUTH` | AK-3 | ⚠️ XFAIL ([BR-03](JIRA_BUG_REPORTS.md)) | `auth`, `regression`, `xfail` | [`test_password_reset.py:98`](../tests/auth/test_password_reset.py#L98) -> `test_tc16_auth_password_reset_mismatched_confirmation` |
| **AUTH** | [`US-06`](požadavky_ust_podle_src.md) | `TC-17-AUTH` | AK-1, AK-2 | 🟢 Pokryto | `auth`, `regression` | [`test_password_reset.py:130`](../tests/auth/test_password_reset.py#L130) -> `test_tc17_auth_email_verification_success` |
| **AUTH** | [`US-06`](požadavky_ust_podle_src.md) | `TC-18-AUTH` | AK-3 | 🟢 Pokryto | `auth`, `regression` | [`test_password_reset.py:139`](../tests/auth/test_password_reset.py#L139) -> `test_tc18_auth_email_verification_invalid_link` |
| **AUTH** | [`US-06`](požadavky_ust_podle_src.md) | `TC-19-AUTH` | AK-4, AK-5 | 🟢 Pokryto | `auth`, `regression` | [`test_password_reset.py:147`](../tests/auth/test_password_reset.py#L147) -> `test_tc19_auth_resend_verification_email_rate_limit` |
| **AUTH** | [`US-07`](požadavky_ust_podle_src.md) | `TC-20-AUTH` | AK-1, AK-2, AK-3 | 🟢 Pokryto | `auth`, `smoke` | [`test_login.py:180`](../tests/auth/test_login.py#L180) -> `test_tc20_auth_temporary_lockout_after_five_failed_logins` |
| **AUTH** | [`US-07`](požadavky_ust_podle_src.md) | `TC-21-AUTH` | AK-4 | 🟢 Pokryto | `auth`, `regression` | [`test_login.py:216`](../tests/auth/test_login.py#L216) -> `test_tc21_auth_reset_failed_login_counter_on_success` |
| **CRS** | [`US-08`](požadavky_ust_podle_src.md) | `TC-22-CRS` | AK-1, AK-5 | 🟢 Pokryto | `courses`, `smoke` | [`test_courses.py:26`](../tests/courses/test_courses.py#L26) -> `test_tc22_crs_catalog_display_for_guest` |
| **CRS** | [`US-08`](požadavky_ust_podle_src.md) | `TC-23-CRS` | AK-2, AK-3, AK-4 | 🟢 Pokryto | `courses`, `regression` | [`test_courses.py:40`](../tests/courses/test_courses.py#L40) -> `test_tc23_crs_course_card_attributes` |
| **CRS** | [`US-09`](požadavky_ust_podle_src.md) | `TC-24-CRS` | AK-1, AK-2, AK-3, AK-4 | 🟢 Pokryto | `courses`, `smoke` | [`test_courses.py:60`](../tests/courses/test_courses.py#L60) -> `test_tc24_crs_course_detail_and_iterations_display` |
| **CRS** | [`US-10`](požadavky_ust_podle_src.md) | `TC-25-CRS` | AK-1, AK-2 | 🟢 Pokryto | `courses`, `smoke` | [`test_courses.py:85`](../tests/courses/test_courses.py#L85) -> `test_tc25_crs_enrollment_button_for_available_capacity` |
| **CRS** | [`US-10`](požadavky_ust_podle_src.md) | `TC-26-CRS` | AK-3 | 🟢 Pokryto | `courses`, `regression` | [`test_courses.py:104`](../tests/courses/test_courses.py#L104) -> `test_tc26_crs_indication_when_capacity_full_or_unauthenticated` |
| **ENR** | [`US-11`](požadavky_ust_podle_src.md) | `TC-27-ENR` | AK-1, AK-5, AK-6, AK-7 | 🟢 Pokryto | `enrollment`, `smoke` | [`test_enrollment.py:35`](../tests/enrollment/test_enrollment.py#L35) -> `test_tc27_enr_successful_enrollment_with_ico_and_phone` |
| **ENR** | [`US-11`](požadavky_ust_podle_src.md) | `TC-28-ENR` | AK-1, AK-3 | ⚠️ XFAIL ([Defekt](JIRA_BUG_REPORTS.md)) | `enrollment`, `regression`, `xfail` | [`test_enrollment.py:69`](../tests/enrollment/test_enrollment.py#L69) -> `test_tc28_enr_successful_enrollment_without_ico` |
| **ENR** | [`US-11`](požadavky_ust_podle_src.md) | `TC-29-ENR` | AK-3, AK-4 | 🟢 Pokryto | `enrollment`, `regression` | [`test_enrollment.py:94`](../tests/enrollment/test_enrollment.py#L94) -> `test_tc29_enr_invalid_ico_validation` |
| **ENR** | [`US-11`](požadavky_ust_podle_src.md) | `TC-30-ENR` | AK-2, AK-4 | 🟢 Pokryto | `enrollment`, `regression` | [`test_enrollment.py:111`](../tests/enrollment/test_enrollment.py#L111) -> `test_tc30_enr_short_phone_validation` |
| **ENR** | [`US-12`](požadavky_ust_podle_src.md) | `TC-31-ENR` | AK-1 až AK-8 | 🟢 Pokryto | `enrollment`, `smoke` | [`test_enrollment.py:127`](../tests/enrollment/test_enrollment.py#L127) -> `test_tc31_enr_my_courses_overview_display` |
| **LEC** | [`US-13`](požadavky_ust_podle_src.md) | `TC-32-LEC` | AK-1, AK-2, AK-4, AK-6 | 🟢 Pokryto | `lecturer`, `smoke` | [`test_lecturer.py:35`](../tests/lecturer/test_lecturer.py#L35) -> `test_tc32_lec_create_course_with_16_9_aspect_ratio_image` |
| **LEC** | [`US-13`](požadavky_ust_podle_src.md) | `TC-33-LEC` | AK-5 | ⚠️ XFAIL ([Defekt](JIRA_BUG_REPORTS.md)) | `lecturer`, `regression`, `xfail` | [`test_lecturer.py:60`](../tests/lecturer/test_lecturer.py#L60) -> `test_tc33_lec_reject_invalid_aspect_ratio_image` |
| **LEC** | [`US-13`](požadavky_ust_podle_src.md) | `TC-34-LEC` | AK-2, AK-3 | ⚠️ XFAIL ([Defekt](JIRA_BUG_REPORTS.md)) | `lecturer`, `regression`, `xfail` | [`test_lecturer.py:81`](../tests/lecturer/test_lecturer.py#L81) -> `test_tc34_lec_validation_required_fields_and_numeric_values` |
| **LEC** | [`US-14`](požadavky_ust_podle_src.md) | `TC-35-LEC` | AK-1, AK-2, AK-4, AK-5 | 🟢 Pokryto | `lecturer`, `regression` | [`test_lecturer.py:99`](../tests/lecturer/test_lecturer.py#L99) -> `test_tc35_lec_create_course_iteration_by_lecturer` |
| **LEC** | [`US-14`](požadavky_ust_podle_src.md) | `TC-36-LEC` | AK-3 | ⚠️ XFAIL ([Defekt](JIRA_BUG_REPORTS.md)) | `lecturer`, `regression`, `xfail` | [`test_lecturer.py:127`](../tests/lecturer/test_lecturer.py#L127) -> `test_tc36_lec_validation_iteration_required_fields` |
| **LEC** | [`US-15`](požadavky_ust_podle_src.md) | `TC-37-LEC` | AK-1, AK-2, AK-3 | 🟢 Pokryto | `auth`, `smoke`, `lecturer` | [`test_login.py:67`](../tests/auth/test_login.py#L67) -> `test_tc37_lec_lecturer_successful_login_and_rights` |
| **LEC** | [`US-15`](požadavky_ust_podle_src.md) | `TC-38-LEC` | AK-4 | ⚠️ XFAIL ([BR-01](JIRA_BUG_REPORTS.md)) | `lecturer`, `smoke`, `xfail` | [`test_lecturer.py:189`](../tests/lecturer/test_lecturer.py#L189) -> `test_tc38_lec_customer_cannot_access_lecturer_create_course` |
| **PRF** | [`US-16`](požadavky_ust_podle_src.md) | `TC-39-PRF` | AK-1, AK-2 | 🟢 Pokryto | `profile`, `smoke` | [`test_profile.py:29`](../tests/profile/test_profile.py#L29) -> `test_tc39_prf_personalized_welcome_dashboard` |
| **PRF** | [`US-17`](požadavky_ust_podle_src.md) | `TC-40-PRF` | AK-1, AK-3, AK-6 | 🟢 Pokryto | `profile`, `smoke` | [`test_profile.py:38`](../tests/profile/test_profile.py#L38) -> `test_tc40_prf_display_and_update_profile` |
| **PRF** | [`US-17`](požadavky_ust_podle_src.md) | `TC-41-PRF` | AK-4, AK-5 | 🟢 Pokryto | `profile`, `regression` | [`test_profile.py:65`](../tests/profile/test_profile.py#L65) -> `test_tc41_prf_ico_and_phone_validation_in_profile` |
| **PRF** | [`US-17`](požadavky_ust_podle_src.md) | `TC-42-PRF` | AK-2 | 🟢 Pokryto | `profile`, `regression` | [`test_profile.py:77`](../tests/profile/test_profile.py#L77) -> `test_tc42_prf_duplicate_email_change_rejected` |
| **SEC** | [`US-18`](požadavky_ust_podle_src.md) | `TC-43-SEC` | AK-1, AK-2, AK-6, AK-7 | 🟢 Pokryto | `security`, `smoke` | [`test_security.py:29`](../tests/security/test_security.py#L29) -> `test_tc43_sec_unauthenticated_private_url_access_blocked` |
| **SEC** | [`US-18`](požadavky_ust_podle_src.md) | `TC-44-SEC` | AK-3, AK-4 | ⚠️ XFAIL ([BR-01](JIRA_BUG_REPORTS.md)) | `security`, `smoke`, `xfail` | [`test_security.py:45`](../tests/security/test_security.py#L45) -> `test_tc44_sec_customer_cannot_access_lecturer_operations` |
| **SEC** | [`US-18`](požadavky_ust_podle_src.md) | `TC-45-SEC` | AK-5 | 🟢 Pokryto | `security`, `regression` | [`test_security.py:57`](../tests/security/test_security.py#L57) -> `test_tc45_sec_lecturer_cannot_enroll_as_customer` |
| **SEC** | [`US-19`](požadavky_ust_podle_src.md) | `TC-46-SEC` | AK-1, AK-2 | 🟢 Pokryto | `security`, `smoke` | [`test_security.py:69`](../tests/security/test_security.py#L69) -> `test_tc46_sec_csrf_cookie_present_for_stateful_forms` |
| **SEC** | [`US-19`](požadavky_ust_podle_src.md) | `TC-47-SEC` | AK-3 | 🟢 Pokryto | `security`, `regression` | [`test_security.py:84`](../tests/security/test_security.py#L84) -> `test_tc47_sec_session_regeneration_on_login_and_logout` |
| **ENR** | [`US-12`](požadavky_ust_podle_src.md) | `TC-48-ENR` | AK-1, AK-2 | 🟢 Pokryto | `enrollment`, `regression` | [`test_enrollment.py:173`](../tests/enrollment/test_enrollment.py#L173) -> `test_tc48_enr_empty_state_my_courses_without_enrollments` |
