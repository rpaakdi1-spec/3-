--
-- PostgreSQL database dump
--

\restrict fHS72CWYc590y619DIAduvPv1t0If43Fd8dNaVrwe3FXgGazTnEHHZek25uN2g7

-- Dumped from database version 15.15
-- Dumped by pg_dump version 15.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: ai_chat_histories; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.ai_chat_histories (id, user_id, session_id, user_message, assistant_message, intent, action, parsed_order, parsed_orders, dispatch_recommendation, created_at) FROM stdin;
\.


--
-- Data for Name: ai_usage_logs; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.ai_usage_logs (id, user_id, session_id, model_name, provider, prompt_tokens, completion_tokens, total_tokens, prompt_cost, completion_cost, total_cost, response_time_ms, status, error_message, intent, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.users (id, username, email, hashed_password, full_name, role, is_active, is_superuser, created_at, updated_at, last_login) FROM stdin;
1	admin	admin@uvis.com	$2b$12$.I.QbUAVmSaLpf1DWfDWx.cmmLAswyfrzwycmOkTnaIEr.Nr988pq	System Administrator	ADMIN	t	t	2026-02-06 10:55:55.010415+00	2026-02-06 10:58:17.41204+00	2026-02-06 10:58:17.797404+00
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.audit_logs (id, user_id, action, resource_type, resource_id, details, ip_address, user_agent, status, created_at) FROM stdin;
\.


--
-- Data for Name: band_chat_rooms; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.band_chat_rooms (id, name, band_url, description, is_active, last_message_at, total_messages, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: drivers; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.drivers (code, name, phone, emergency_contact, work_start_time, work_end_time, max_work_hours, license_number, license_type, notes, is_active, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: vehicles; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.vehicles (code, plate_number, vehicle_type, uvis_device_id, uvis_enabled, max_pallets, max_weight_kg, max_volume_cbm, forklift_operator_available, tonnage, length_m, width_m, height_m, driver_name, driver_phone, min_temp_celsius, max_temp_celsius, fuel_efficiency_km_per_liter, fuel_cost_per_liter, status, garage_address, garage_latitude, garage_longitude, notes, is_active, is_emergency, emergency_type, emergency_severity, emergency_reported_at, emergency_location, emergency_description, estimated_repair_time, replacement_vehicle_id, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: dispatches; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.dispatches (dispatch_number, dispatch_date, vehicle_id, driver_id, total_orders, total_pallets, total_weight_kg, total_distance_km, empty_distance_km, estimated_duration_minutes, estimated_cost, status, is_scheduled, scheduled_for_date, auto_confirm_at, is_recurring, recurring_pattern, recurring_days, is_urgent, urgency_level, urgent_reason, optimization_score, ai_metadata, notes, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: band_message_schedules; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.band_message_schedules (id, dispatch_id, is_active, start_time, end_time, min_interval_seconds, max_interval_seconds, messages_generated, last_generated_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: band_messages; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.band_messages (id, dispatch_id, message_content, message_type, is_sent, sent_at, generated_at, scheduled_for, variation_seed) FROM stdin;
\.


--
-- Data for Name: clients; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.clients (code, name, client_type, address, address_detail, latitude, longitude, geocoded, geocode_error, pickup_start_time, pickup_end_time, delivery_start_time, delivery_end_time, forklift_operator_available, loading_time_minutes, contact_person, phone, notes, is_active, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: billing_policies; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.billing_policies (id, client_id, billing_cycle, billing_day, payment_terms_days, base_rate_per_km, base_rate_per_pallet, base_rate_per_kg, weekend_surcharge_rate, night_surcharge_rate, express_surcharge_rate, temperature_control_rate, volume_discount_threshold, volume_discount_rate, is_active, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.orders (order_number, order_date, temperature_zone, pickup_client_id, delivery_client_id, pickup_address, pickup_address_detail, pickup_latitude, pickup_longitude, delivery_address, delivery_address_detail, delivery_latitude, delivery_longitude, pallet_count, weight_kg, volume_cbm, product_name, product_code, pickup_start_time, pickup_end_time, delivery_start_time, delivery_end_time, requested_delivery_date, is_reserved, reserved_at, confirmed_at, recurring_type, recurring_end_date, priority, requires_forklift, is_stackable, status, notes, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: dispatch_routes; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.dispatch_routes (dispatch_id, sequence, route_type, order_id, location_name, address, latitude, longitude, distance_from_previous_km, duration_from_previous_minutes, estimated_arrival_time, estimated_work_duration_minutes, estimated_departure_time, current_pallets, current_weight_kg, notes, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: driver_schedules; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.driver_schedules (id, driver_id, schedule_date, schedule_type, start_time, end_time, is_available, notes, requires_approval, is_approved, approved_by, approval_notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: driver_settlements; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.driver_settlements (id, settlement_number, driver_id, settlement_period_start, settlement_period_end, total_revenue, commission_amount, expense_amount, net_amount, is_paid, paid_date, dispatch_count, total_distance_km, total_pallets, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: driver_settlement_items; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.driver_settlement_items (id, settlement_id, dispatch_id, revenue, commission_rate, commission_amount, distance_km, pallets, created_at) FROM stdin;
\.


--
-- Data for Name: fcm_tokens; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.fcm_tokens (id, user_id, token, device_type, device_id, app_version, is_active, last_used_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: invoices; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.invoices (id, invoice_number, client_id, billing_period_start, billing_period_end, subtotal, tax_amount, discount_amount, total_amount, paid_amount, status, issue_date, due_date, paid_date, notes, pdf_url, sent_at, created_at, updated_at, created_by) FROM stdin;
\.


--
-- Data for Name: invoice_line_items; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.invoice_line_items (id, invoice_id, dispatch_id, description, quantity, unit_price, amount, distance_km, pallets, weight_kg, surcharge_amount, discount_amount, created_at) FROM stdin;
\.


--
-- Data for Name: vehicle_maintenance_records; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.vehicle_maintenance_records (maintenance_number, vehicle_id, maintenance_type, status, priority, scheduled_date, started_at, completed_at, odometer_reading, service_center, service_center_contact, service_center_address, mechanic_name, assigned_by, labor_cost, parts_cost, total_cost, description, findings, recommendations, notes, invoice_number, invoice_file_path, before_photos, after_photos, next_maintenance_date, next_maintenance_odometer, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: vehicle_parts; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.vehicle_parts (part_number, part_name, category, manufacturer, model, quantity_in_stock, minimum_stock, unit, unit_price, supplier, supplier_contact, compatible_models, average_lifespan_km, average_lifespan_months, description, notes, is_active, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: maintenance_part_usage; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.maintenance_part_usage (maintenance_record_id, part_id, quantity_used, unit_price, total_price, notes, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: maintenance_schedules; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.maintenance_schedules (vehicle_id, maintenance_type, interval_km, interval_months, last_maintenance_date, last_maintenance_odometer, next_maintenance_date, next_maintenance_odometer, alert_before_km, alert_before_days, is_active, is_overdue, notes, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: notices; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.notices (id, title, content, author, image_url, is_important, views, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: notification_templates; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.notification_templates (id, template_code, template_name, notification_type, channel, title_template, message_template, kakao_template_id, kakao_button_json, description, variables, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.notifications (id, notification_type, channel, status, recipient_name, recipient_phone, recipient_email, recipient_device_token, title, message, template_code, notification_metadata, sent_at, delivered_at, read_at, external_id, external_response, error_message, retry_count, order_id, dispatch_id, vehicle_id, driver_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: order_templates; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.order_templates (id, name, description, category, temperature_zone, pickup_client_id, pickup_address, pickup_address_detail, delivery_client_id, delivery_address, delivery_address_detail, pallet_count, weight_kg, volume_cbm, product_name, product_code, pickup_start_time, pickup_end_time, delivery_start_time, delivery_end_time, requires_forklift, is_stackable, priority, notes, usage_count, last_used_at, is_shared, created_by, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.payments (id, payment_number, invoice_id, amount, payment_method, payment_date, reference_number, bank_name, account_number, notes, receipt_url, created_at, updated_at, created_by) FROM stdin;
\.


--
-- Data for Name: purchase_orders; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.purchase_orders (id, title, content, image_urls, author, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: push_notification_logs; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.push_notification_logs (id, user_id, token, title, body, data_json, notification_type, status, error_message, sent_at) FROM stdin;
\.


--
-- Data for Name: recurring_orders; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.recurring_orders (id, name, description, frequency, start_date, end_date, weekdays, day_of_month, temperature_zone, pickup_client_id, delivery_client_id, pickup_address, pickup_address_detail, delivery_address, delivery_address_detail, pallet_count, weight_kg, volume_cbm, product_name, product_code, pickup_start_time, pickup_end_time, delivery_start_time, delivery_end_time, priority, requires_forklift, is_stackable, notes, is_active, last_generated_date, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: security_alerts; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.security_alerts (id, user_id, alert_type, severity, description, ip_address, user_agent, is_resolved, resolved_by, resolved_at, created_at) FROM stdin;
\.


--
-- Data for Name: vehicle_locations; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.vehicle_locations (id, vehicle_id, dispatch_id, latitude, longitude, accuracy, altitude, speed, heading, temperature_celsius, humidity_percent, uvis_device_id, uvis_timestamp, recorded_at, is_ignition_on, battery_voltage, fuel_level_percent, odometer_km, address, notes) FROM stdin;
\.


--
-- Data for Name: temperature_alerts; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.temperature_alerts (id, vehicle_id, dispatch_id, location_id, alert_type, severity, temperature_celsius, threshold_min, threshold_max, detected_at, resolved_at, is_resolved, notification_sent, notification_channels, message, notes) FROM stdin;
\.


--
-- Data for Name: two_factor_auth; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.two_factor_auth (id, user_id, secret_key, is_enabled, backup_codes, created_at, last_used_at) FROM stdin;
\.


--
-- Data for Name: two_factor_logs; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.two_factor_logs (id, user_id, action, ip_address, user_agent, success, created_at) FROM stdin;
\.


--
-- Data for Name: uvis_access_keys; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.uvis_access_keys (id, serial_key, access_key, issued_at, expires_at, is_active, created_at, updated_at) FROM stdin;
1	S1910-3A84-4559--CC4	cddbeeab18c968f3a6d77ada6884ba65abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-05 14:25:07.36034+00	2026-02-05 14:30:07.36034+00	f	2026-02-05 14:25:07.364052+00	2026-02-05 14:30:07.637231+00
2	S1910-3A84-4559--CC4	20dbbee3a74feed8be4b13e033cfd238abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-05 14:30:07.634448+00	2026-02-05 14:35:07.634448+00	f	2026-02-05 14:30:07.637231+00	2026-02-06 09:46:32.524731+00
3	S1910-3A84-4559--CC4	3f7040069a1effcad63723a973c3195aabc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 09:46:32.521765+00	2026-02-06 09:51:32.521765+00	f	2026-02-06 09:46:32.524731+00	2026-02-06 09:46:32.563378+00
4	S1910-3A84-4559--CC4	3f7040069a1effcad63723a973c3195aabc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 09:46:32.538373+00	2026-02-06 09:51:32.538373+00	f	2026-02-06 09:46:32.540739+00	2026-02-06 09:46:32.563378+00
5	S1910-3A84-4559--CC4	3f7040069a1effcad63723a973c3195aabc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 09:46:32.561476+00	2026-02-06 09:51:32.561476+00	f	2026-02-06 09:46:32.563378+00	2026-02-06 09:46:33.549589+00
6	S1910-3A84-4559--CC4	ae02d647c6810daf7580c9e78df93ae5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 09:46:33.546927+00	2026-02-06 09:51:33.546927+00	f	2026-02-06 09:46:33.549589+00	2026-02-06 09:56:32.52711+00
7	S1910-3A84-4559--CC4	840fb98646eab4226934b09508efba96abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 09:56:32.525891+00	2026-02-06 10:01:32.525891+00	f	2026-02-06 09:56:32.52711+00	2026-02-06 09:56:32.574913+00
8	S1910-3A84-4559--CC4	840fb98646eab4226934b09508efba96abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 09:56:32.526538+00	2026-02-06 10:01:32.526538+00	f	2026-02-06 09:56:32.527905+00	2026-02-06 09:56:32.574913+00
9	S1910-3A84-4559--CC4	840fb98646eab4226934b09508efba96abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 09:56:32.573135+00	2026-02-06 10:01:32.573135+00	f	2026-02-06 09:56:32.574913+00	2026-02-06 09:56:32.632042+00
10	S1910-3A84-4559--CC4	840fb98646eab4226934b09508efba96abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 09:56:32.63071+00	2026-02-06 10:01:32.63071+00	f	2026-02-06 09:56:32.632042+00	2026-02-06 10:05:14.288001+00
11	S1910-3A84-4559--CC4	7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:05:14.285855+00	2026-02-06 10:10:14.285855+00	f	2026-02-06 10:05:14.288001+00	2026-02-06 10:05:14.291104+00
12	S1910-3A84-4559--CC4	7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:05:14.284085+00	2026-02-06 10:10:14.284085+00	f	2026-02-06 10:05:14.291104+00	2026-02-06 10:15:14.021026+00
13	S1910-3A84-4559--CC4	7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:05:14.278969+00	2026-02-06 10:10:14.278969+00	f	2026-02-06 10:05:14.288614+00	2026-02-06 10:15:14.021026+00
14	S1910-3A84-4559--CC4	7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:05:14.289052+00	2026-02-06 10:10:14.289052+00	f	2026-02-06 10:05:14.292059+00	2026-02-06 10:15:14.021026+00
15	S1910-3A84-4559--CC4	0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:15:14.019248+00	2026-02-06 10:20:14.019248+00	f	2026-02-06 10:15:14.021026+00	2026-02-06 10:15:14.062403+00
16	S1910-3A84-4559--CC4	0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:15:14.060994+00	2026-02-06 10:20:14.060994+00	f	2026-02-06 10:15:14.062403+00	2026-02-06 10:15:14.070764+00
17	S1910-3A84-4559--CC4	0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:15:14.069213+00	2026-02-06 10:20:14.069213+00	f	2026-02-06 10:15:14.070764+00	2026-02-06 10:15:14.079216+00
18	S1910-3A84-4559--CC4	0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:15:14.078035+00	2026-02-06 10:20:14.078035+00	f	2026-02-06 10:15:14.079216+00	2026-02-06 10:25:14.082146+00
19	S1910-3A84-4559--CC4	a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:25:14.080982+00	2026-02-06 10:30:14.080982+00	f	2026-02-06 10:25:14.082146+00	2026-02-06 10:25:14.133326+00
20	S1910-3A84-4559--CC4	a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:25:14.080978+00	2026-02-06 10:30:14.080978+00	f	2026-02-06 10:25:14.082438+00	2026-02-06 10:25:14.133326+00
21	S1910-3A84-4559--CC4	a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:25:14.132105+00	2026-02-06 10:30:14.132105+00	f	2026-02-06 10:25:14.133326+00	2026-02-06 10:25:14.136369+00
22	S1910-3A84-4559--CC4	a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:25:14.134985+00	2026-02-06 10:30:14.134985+00	f	2026-02-06 10:25:14.136369+00	2026-02-06 10:35:14.081141+00
23	S1910-3A84-4559--CC4	e7b3e4a38f891f6fbae261bc57f811e5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:35:14.080142+00	2026-02-06 10:40:14.080142+00	f	2026-02-06 10:35:14.081141+00	2026-02-06 10:35:14.123291+00
24	S1910-3A84-4559--CC4	e7b3e4a38f891f6fbae261bc57f811e5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:35:14.085843+00	2026-02-06 10:40:14.085843+00	f	2026-02-06 10:35:14.086862+00	2026-02-06 10:35:14.123291+00
25	S1910-3A84-4559--CC4	e7b3e4a38f891f6fbae261bc57f811e5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:35:14.121249+00	2026-02-06 10:40:14.121249+00	f	2026-02-06 10:35:14.123291+00	2026-02-06 10:35:14.13822+00
26	S1910-3A84-4559--CC4	e7b3e4a38f891f6fbae261bc57f811e5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:35:14.120138+00	2026-02-06 10:40:14.120138+00	f	2026-02-06 10:35:14.13822+00	2026-02-06 10:52:02.845533+00
27	S1910-3A84-4559--CC4	77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:52:02.841804+00	2026-02-06 10:57:02.841804+00	f	2026-02-06 10:52:02.845533+00	2026-02-06 10:52:02.853674+00
28	S1910-3A84-4559--CC4	77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:52:02.849362+00	2026-02-06 10:57:02.849362+00	f	2026-02-06 10:52:02.851292+00	2026-02-06 10:52:02.867993+00
29	S1910-3A84-4559--CC4	77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:52:02.851448+00	2026-02-06 10:57:02.851448+00	f	2026-02-06 10:52:02.853674+00	2026-02-06 10:52:02.867993+00
30	S1910-3A84-4559--CC4	77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5	2026-02-06 10:52:02.866127+00	2026-02-06 10:57:02.866127+00	t	2026-02-06 10:52:02.867993+00	\N
\.


--
-- Data for Name: uvis_api_logs; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.uvis_api_logs (id, api_type, method, url, request_params, response_status, response_data, error_message, execution_time_ms, created_at) FROM stdin;
1	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=cddbeeab18c968f3a6d77ada6884ba65abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "cddbeeab18c968f3a6d77ada6884ba65abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"3.0","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"127.027912","OFF_KEY":"0013668","ID":2,"TPL_TIME":"223326","TPL_DATE":"20260205","TPL_X_POSITION":"37.114276"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"202602	\N	31	2026-02-05 14:25:07.405389+00
2	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=cddbeeab18c968f3a6d77ada6884ba65abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "cddbeeab18c968f3a6d77ada6884ba65abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"3.0","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"127.027912","OFF_KEY":"0013668","ID":2,"TPL_TIME":"223326","TPL_DATE":"20260205","TPL_X_POSITION":"37.114276"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"202602	\N	83	2026-02-05 14:25:07.492124+00
3	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=cddbeeab18c968f3a6d77ada6884ba65abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "cddbeeab18c968f3a6d77ada6884ba65abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	유효하지 않은 요청입니다.\r\n	\N	120	2026-02-05 14:30:07.251159+00
4	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do	{"method": "getDeviceAPI", "AccessKey": "cddbeeab18c968f3a6d77ada6884ba65abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	\N	\N	Expecting value: line 1 column 1 (char 0)	\N	2026-02-05 14:30:07.379484+00
5	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=20dbbee3a74feed8be4b13e033cfd238abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "20dbbee3a74feed8be4b13e033cfd238abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"3.0","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"127.027912","OFF_KEY":"0013668","ID":2,"TPL_TIME":"223326","TPL_DATE":"20260205","TPL_X_POSITION":"37.114276"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"202602	\N	32	2026-02-05 14:30:07.67784+00
6	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=3f7040069a1effcad63723a973c3195aabc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "3f7040069a1effcad63723a973c3195aabc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.9","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"184326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	41	2026-02-06 09:46:32.595451+00
7	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=3f7040069a1effcad63723a973c3195aabc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "3f7040069a1effcad63723a973c3195aabc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.9","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"184326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	38	2026-02-06 09:46:32.596923+00
8	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=3f7040069a1effcad63723a973c3195aabc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "3f7040069a1effcad63723a973c3195aabc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.9","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"184326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	63	2026-02-06 09:46:32.632726+00
9	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=ae02d647c6810daf7580c9e78df93ae5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "ae02d647c6810daf7580c9e78df93ae5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.9","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"184326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	884	2026-02-06 09:46:34.442386+00
10	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=ae02d647c6810daf7580c9e78df93ae5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "ae02d647c6810daf7580c9e78df93ae5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.9","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"184826","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	141	2026-02-06 09:51:32.376609+00
12	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=ae02d647c6810daf7580c9e78df93ae5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "ae02d647c6810daf7580c9e78df93ae5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.9","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"184826","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	149	2026-02-06 09:51:32.372645+00
14	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=840fb98646eab4226934b09508efba96abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "840fb98646eab4226934b09508efba96abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.8","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"185326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	33	2026-02-06 09:56:32.565576+00
25	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do	{"method": "getDeviceAPI", "AccessKey": "7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	\N	\N	Expecting value: line 1 column 1 (char 0)	\N	2026-02-06 10:10:14.063084+00
26	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do	{"method": "getDeviceAPI", "AccessKey": "7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	\N	\N	Expecting value: line 1 column 1 (char 0)	\N	2026-02-06 10:10:14.064457+00
65	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do	{"method": "getDeviceAPI", "AccessKey": "77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	\N	\N	Expecting value: line 1 column 1 (char 0)	\N	2026-02-06 10:57:02.826662+00
11	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=ae02d647c6810daf7580c9e78df93ae5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "ae02d647c6810daf7580c9e78df93ae5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.9","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"184826","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	142	2026-02-06 09:51:32.375666+00
16	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=840fb98646eab4226934b09508efba96abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "840fb98646eab4226934b09508efba96abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.8","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"185326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	49	2026-02-06 09:56:32.629763+00
13	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=ae02d647c6810daf7580c9e78df93ae5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "ae02d647c6810daf7580c9e78df93ae5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.9","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"184826","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	148	2026-02-06 09:51:32.374347+00
17	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=840fb98646eab4226934b09508efba96abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "840fb98646eab4226934b09508efba96abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.8","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"185326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	32	2026-02-06 09:56:32.667082+00
15	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=840fb98646eab4226934b09508efba96abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "840fb98646eab4226934b09508efba96abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.8","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"185326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	40	2026-02-06 09:56:32.574165+00
18	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.8","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"190326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	57	2026-02-06 10:05:14.357778+00
19	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.8","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"190326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	61	2026-02-06 10:05:14.359764+00
20	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.8","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"190326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	58	2026-02-06 10:05:14.360372+00
21	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.8","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"190326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	59	2026-02-06 10:05:14.361099+00
23	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	유효하지 않은 요청입니다.\r\n	\N	115	2026-02-06 10:10:13.937757+00
24	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	유효하지 않은 요청입니다.\r\n	\N	117	2026-02-06 10:10:13.940198+00
22	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.7","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"190826","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	99	2026-02-06 10:10:13.934058+00
31	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.7","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"191326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	32	2026-02-06 10:15:14.115473+00
36	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	유효하지 않은 요청입니다.\r\n	\N	127	2026-02-06 10:20:13.927738+00
38	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do	{"method": "getDeviceAPI", "AccessKey": "0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	\N	\N	Expecting value: line 1 column 1 (char 0)	\N	2026-02-06 10:20:14.058598+00
43	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.6","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"192326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	63	2026-02-06 10:25:14.201614+00
45	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	유효하지 않은 요청입니다.\r\n	\N	115	2026-02-06 10:30:13.936788+00
49	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do	{"method": "getDeviceAPI", "AccessKey": "a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	\N	\N	Expecting value: line 1 column 1 (char 0)	\N	2026-02-06 10:30:14.060834+00
27	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	유효하지 않은 요청입니다.\r\n	\N	125	2026-02-06 10:10:13.942926+00
28	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do	{"method": "getDeviceAPI", "AccessKey": "7a3510362ef381d11c25ab3dcded0590abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	\N	\N	Expecting value: line 1 column 1 (char 0)	\N	2026-02-06 10:10:14.073102+00
30	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.7","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"191326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	27	2026-02-06 10:15:14.10454+00
39	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	유효하지 않은 요청입니다.\r\n	\N	209	2026-02-06 10:20:13.94225+00
40	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do	{"method": "getDeviceAPI", "AccessKey": "0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	\N	\N	Expecting value: line 1 column 1 (char 0)	\N	2026-02-06 10:20:14.160498+00
44	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.6","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"192326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	75	2026-02-06 10:25:14.216431+00
51	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	유효하지 않은 요청입니다.\r\n	\N	124	2026-02-06 10:30:13.94046+00
52	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do	{"method": "getDeviceAPI", "AccessKey": "a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	\N	\N	Expecting value: line 1 column 1 (char 0)	\N	2026-02-06 10:30:14.068553+00
29	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.7","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"191326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	47	2026-02-06 10:15:14.077886+00
33	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	유효하지 않은 요청입니다.\r\n	\N	126	2026-02-06 10:20:13.923409+00
35	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do	{"method": "getDeviceAPI", "AccessKey": "0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	\N	\N	Expecting value: line 1 column 1 (char 0)	\N	2026-02-06 10:20:14.054223+00
42	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.6","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"192326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	46	2026-02-06 10:25:14.135959+00
46	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	유효하지 않은 요청입니다.\r\n	\N	120	2026-02-06 10:30:13.933141+00
48	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do	{"method": "getDeviceAPI", "AccessKey": "a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	\N	\N	Expecting value: line 1 column 1 (char 0)	\N	2026-02-06 10:30:14.060837+00
32	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.7","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"191326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	62	2026-02-06 10:15:14.129918+00
34	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	유효하지 않은 요청입니다.\r\n	\N	118	2026-02-06 10:20:13.933558+00
37	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do	{"method": "getDeviceAPI", "AccessKey": "0e8f566629a14a5ac5a4948220ae3340abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	\N	\N	Expecting value: line 1 column 1 (char 0)	\N	2026-02-06 10:20:14.058353+00
41	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.6","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"192326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	46	2026-02-06 10:25:14.136002+00
47	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	유효하지 않은 요청입니다.\r\n	\N	125	2026-02-06 10:30:13.932745+00
50	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do	{"method": "getDeviceAPI", "AccessKey": "a868c63a267c92851c42e513148daee5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	\N	\N	Expecting value: line 1 column 1 (char 0)	\N	2026-02-06 10:30:14.064177+00
53	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=e7b3e4a38f891f6fbae261bc57f811e5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "e7b3e4a38f891f6fbae261bc57f811e5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.5","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"193326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	29	2026-02-06 10:35:14.122862+00
54	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=e7b3e4a38f891f6fbae261bc57f811e5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "e7b3e4a38f891f6fbae261bc57f811e5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.5","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"193326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	34	2026-02-06 10:35:14.129628+00
63	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	유효하지 않은 요청입니다.\r\n	\N	117	2026-02-06 10:57:02.703463+00
66	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do	{"method": "getDeviceAPI", "AccessKey": "77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	\N	\N	Expecting value: line 1 column 1 (char 0)	\N	2026-02-06 10:57:02.828336+00
55	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=e7b3e4a38f891f6fbae261bc57f811e5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "e7b3e4a38f891f6fbae261bc57f811e5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.5","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"193326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	35	2026-02-06 10:35:14.167333+00
56	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=e7b3e4a38f891f6fbae261bc57f811e5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "e7b3e4a38f891f6fbae261bc57f811e5abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.5","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"0.000000","OFF_KEY":"0013668","ID":2,"TPL_TIME":"193326","TPL_DATE":"20260206","TPL_X_POSITION":"0.000000"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"20260204"	\N	74	2026-02-06 10:35:14.242559+00
57	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.3","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"126.781480","OFF_KEY":"0013668","ID":2,"TPL_TIME":"194826","TPL_DATE":"20260206","TPL_X_POSITION":"35.168472"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"202602	\N	39	2026-02-06 10:52:02.900406+00
58	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.3","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"126.781480","OFF_KEY":"0013668","ID":2,"TPL_TIME":"194826","TPL_DATE":"20260206","TPL_X_POSITION":"35.168472"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"202602	\N	71	2026-02-06 10:52:02.925998+00
59	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.3","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"126.781480","OFF_KEY":"0013668","ID":2,"TPL_TIME":"194826","TPL_DATE":"20260206","TPL_X_POSITION":"35.168472"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"202602	\N	73	2026-02-06 10:52:02.936094+00
61	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	유효하지 않은 요청입니다.\r\n	\N	114	2026-02-06 10:57:02.70356+00
62	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	유효하지 않은 요청입니다.\r\n	\N	116	2026-02-06 10:57:02.703505+00
60	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	[{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"광주85사1706","TPL_DEGREE_A":"3.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"239209332","TPL_Y_POSITION":"127.247848","OFF_KEY":"0013668","ID":1,"TPL_TIME":"160912","TPL_DATE":"20251129","TPL_X_POSITION":"36.973408"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1302","TPL_DEGREE_A":"1.3","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"236275896","TPL_Y_POSITION":"126.781480","OFF_KEY":"0013668","ID":2,"TPL_TIME":"194826","TPL_DATE":"20260206","TPL_X_POSITION":"35.168472"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1303","TPL_DEGREE_A":"OPEN","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"252215336","TPL_Y_POSITION":"127.234824","OFF_KEY":"0013668  ","ID":3,"TPL_TIME":"112103","TPL_DATE":"20260103","TPL_X_POSITION":"36.932868"},{"TPL_DEGREE_B":"NOUSE","CM_NUMBER":"전남87바1304","TPL_DEGREE_A":"0.2","TPL_SIGNAL_B":"0","TPL_SIGNAL_A":"0","TID_ID":"251512430","TPL_Y_POSITION":"127.038917","OFF_KEY":"0013668  ","ID":4,"TPL_TIME":"021432","TPL_DATE":"202602	\N	63	2026-02-06 10:52:02.937695+00
64	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do?method=getDeviceAPI&AccessKey=77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5&GUBUN=02	{"method": "getDeviceAPI", "AccessKey": "77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	200	유효하지 않은 요청입니다.\r\n	\N	120	2026-02-06 10:57:02.703513+00
68	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do	{"method": "getDeviceAPI", "AccessKey": "77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	\N	\N	Expecting value: line 1 column 1 (char 0)	\N	2026-02-06 10:57:02.831464+00
67	temperature	GET	https://s1.u-vis.com/uvisc/SSOAction.do	{"method": "getDeviceAPI", "AccessKey": "77ca2ec0af2ed7995d2c28115efd4050abc7d5548d84978e5ee6293e6a84803c143d9574c7d0613aa140079620bbf8d5", "GUBUN": "02"}	\N	\N	Expecting value: line 1 column 1 (char 0)	\N	2026-02-06 10:57:02.828522+00
\.


--
-- Data for Name: vehicle_gps_logs; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.vehicle_gps_logs (id, vehicle_id, tid_id, bi_date, bi_time, cm_number, bi_turn_onoff, bi_x_position, bi_y_position, bi_gps_speed, latitude, longitude, is_engine_on, speed_kmh, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: vehicle_inspections; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.vehicle_inspections (vehicle_id, inspection_type, inspection_date, expiry_date, result, pass_status, inspection_center, inspector_name, inspection_cost, certificate_number, certificate_file_path, findings, defects, recommendations, notes, id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: vehicle_temperature_logs; Type: TABLE DATA; Schema: public; Owner: uvis_user
--

COPY public.vehicle_temperature_logs (id, vehicle_id, off_key, tid_id, tpl_date, tpl_time, cm_number, tpl_x_position, tpl_y_position, tpl_signal_a, tpl_degree_a, temperature_a, tpl_signal_b, tpl_degree_b, temperature_b, latitude, longitude, created_at, updated_at) FROM stdin;
1	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-05 14:25:07.414013+00	\N
2	\N	0013668	236275896	20260205	223326	전남87바1302	37.114276	127.027912	0	3.0	3	0	NOUSE	\N	37.114276	127.027912	2026-02-05 14:25:07.414013+00	\N
3	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-05 14:25:07.414013+00	\N
4	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-05 14:25:07.414013+00	\N
5	\N	0013668	252227307	20260205	225140	전남87바1305	35.373024	129.018192	1	14.6	-14.6	0	NOUSE	\N	35.373024	129.018192	2026-02-05 14:25:07.414013+00	\N
6	\N	0013668	252214997	20260205	223811	전남87바1313	35.147292	126.759000	0	2.6	2.6	0	NOUSE	\N	35.147292	126.759	2026-02-05 14:25:07.414013+00	\N
7	\N	0013668	252713338	20260205	232024	전남87바1317	35.493013	126.797184	1	22.1	-22.1	0	NOUSE	\N	35.493013	126.797184	2026-02-05 14:25:07.414013+00	\N
8	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-05 14:25:07.414013+00	\N
9	\N	0013668	252214999	20260205	232357	전남87바1320	35.322464	126.814464	0	1.4	1.4	0	NOUSE	\N	35.322464	126.814464	2026-02-05 14:25:07.414013+00	\N
10	\N	0013668	249253808	20260205	232242	전남87바1325	36.156524	126.772072	0	6.2	6.2	0	NOUSE	\N	36.156524	126.772072	2026-02-05 14:25:07.414013+00	\N
11	\N	0013668	252214998	20260205	232037	전남87바1326	37.114520	127.027872	0	4.5	4.5	0	NOUSE	\N	37.11452	127.027872	2026-02-05 14:25:07.414013+00	\N
12	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-05 14:25:07.414013+00	\N
13	\N	0013668	252228119	20260205	232024	전남87바1336	35.814664	127.028472	0	4.0	4	0	NOUSE	\N	35.814664	127.028472	2026-02-05 14:25:07.414013+00	\N
14	\N	0013668	251512431	20260205	232429	전남87바1351	36.086938	127.105187	1	25.4	-25.4	0	NOUSE	\N	36.086938	127.105187	2026-02-05 14:25:07.414013+00	\N
15	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-05 14:25:07.414013+00	\N
16	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-05 14:25:07.414013+00	\N
17	\N	0013668	252227305	20260205	210311	전남87바1361	36.010416	126.798848	0	6.8	6.8	0	NOUSE	\N	36.010416	126.798848	2026-02-05 14:25:07.414013+00	\N
18	\N	0013668	236994200	20260205	125653	전남87바1362	37.087180	127.217069	0	2.6	2.6	0	6.2	6.2	37.08718	127.217069	2026-02-05 14:25:07.414013+00	\N
19	\N	0013668	252215001	20260205	225540	전남87바1364	37.114908	127.026848	0	4.0	4	0	NOUSE	\N	37.114908	127.026848	2026-02-05 14:25:07.414013+00	\N
20	\N	0013668	235771010	20260205	115249	전남87바1367	37.081004	127.207818	1	1.1	-1.1	0	NOUSE	\N	37.081004	127.207818	2026-02-05 14:25:07.414013+00	\N
21	\N	0013668	251512435	20260205	232104	전남87바1368	35.705813	126.755606	1	19.7	-19.7	0	NOUSE	\N	35.705813	126.755606	2026-02-05 14:25:07.414013+00	\N
22	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-05 14:25:07.414013+00	\N
23	\N	0013668	252227304	20260205	212612	전남87바1373	35.240496	127.023824	0	4.8	4.8	0	NOUSE	\N	35.240496	127.023824	2026-02-05 14:25:07.414013+00	\N
24	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-05 14:25:07.414013+00	\N
25	\N	0013668	235980831	20260205	232222	전남87바4156	35.104350	127.249368	1	19.9	-19.9	0	5.4	5.4	35.10435	127.249368	2026-02-05 14:25:07.414013+00	\N
26	\N	0013668	235994979	20260205	232404	전남87바4157	36.306972	127.308440	1	22.6	-22.6	0	NOUSE	\N	36.306972	127.30844	2026-02-05 14:25:07.414013+00	\N
27	\N	0013668	235771783	20260205	095250	전남87바4158	37.139846	127.395104	0	6.4	6.4	0	NOUSE	\N	37.139846	127.395104	2026-02-05 14:25:07.414013+00	\N
28	\N	0013668	252215000	20260205	232324	전남87바4159	35.751456	126.998984	1	17.7	-17.7	0	NOUSE	\N	35.751456	126.998984	2026-02-05 14:25:07.414013+00	\N
29	\N	0013668	252799355	20260203	233337	전남87바4161	35.248084	127.039168	0	2.5	2.5	0	NOUSE	\N	35.248084	127.039168	2026-02-05 14:25:07.414013+00	\N
30	\N	0013668	252227303	20260205	232222	전남87바4162	36.893756	127.189240	0	4.5	4.5	0	NOUSE	\N	36.893756	127.18924	2026-02-05 14:25:07.414013+00	\N
31	\N	0013668	251512429	20260205	232103	전남87바4165	35.348825	127.929377	1	20.3	-20.3	1	0.9	-0.9	35.348825	127.929377	2026-02-05 14:25:07.414013+00	\N
32	\N	0013668	236272742	20260130	173115	전남87바4166	36.006368	127.109768	0	4.5	4.5	0	7.7	7.7	36.006368	127.109768	2026-02-05 14:25:07.414013+00	\N
33	\N	0013668	252214993	20260204	223058	전남87바4169	35.247900	127.038832	0	3.2	3.2	0	NOUSE	\N	35.2479	127.038832	2026-02-05 14:25:07.414013+00	\N
34	\N	0013668	251509223	20260205	202326	전남87바4173	35.507608	128.782341	1	23.1	-23.1	0	NOUSE	\N	35.507608	128.782341	2026-02-05 14:25:07.414013+00	\N
35	\N	0013668	252228112	20260205	232012	전남87바4174	36.765408	127.984432	0	2.0	2	0	NOUSE	\N	36.765408	127.984432	2026-02-05 14:25:07.414013+00	\N
36	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-05 14:25:07.414013+00	\N
37	\N	0013668	252214992	20260205	203512	전남87바4176	35.876952	128.835176	0	2.0	2	0	NOUSE	\N	35.876952	128.835176	2026-02-05 14:25:07.414013+00	\N
38	\N	0013668	239200586	20260205	224946	전남87바4177	35.540326	127.310980	0	5.7	5.7	0	NOUSE	\N	35.540326	127.31098	2026-02-05 14:25:07.414013+00	\N
39	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-05 14:25:07.414013+00	\N
40	\N	0013668	240074478	20260205	201105	전남87바4188	35.248000	127.039472	1	22.8	-22.8	0	NOUSE	\N	35.248	127.039472	2026-02-05 14:25:07.414013+00	\N
41	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-05 14:25:07.414013+00	\N
42	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-05 14:25:07.593217+00	\N
43	\N	0013668	236275896	20260205	223326	전남87바1302	37.114276	127.027912	0	3.0	3	0	NOUSE	\N	37.114276	127.027912	2026-02-05 14:25:07.593217+00	\N
44	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-05 14:25:07.593217+00	\N
45	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-05 14:25:07.593217+00	\N
46	\N	0013668	252227307	20260205	225140	전남87바1305	35.373024	129.018192	1	14.6	-14.6	0	NOUSE	\N	35.373024	129.018192	2026-02-05 14:25:07.593217+00	\N
47	\N	0013668	252214997	20260205	223811	전남87바1313	35.147292	126.759000	0	2.6	2.6	0	NOUSE	\N	35.147292	126.759	2026-02-05 14:25:07.593217+00	\N
48	\N	0013668	252713338	20260205	232024	전남87바1317	35.493013	126.797184	1	22.1	-22.1	0	NOUSE	\N	35.493013	126.797184	2026-02-05 14:25:07.593217+00	\N
49	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-05 14:25:07.593217+00	\N
50	\N	0013668	252214999	20260205	232357	전남87바1320	35.322464	126.814464	0	1.4	1.4	0	NOUSE	\N	35.322464	126.814464	2026-02-05 14:25:07.593217+00	\N
51	\N	0013668	249253808	20260205	232242	전남87바1325	36.156524	126.772072	0	6.2	6.2	0	NOUSE	\N	36.156524	126.772072	2026-02-05 14:25:07.593217+00	\N
52	\N	0013668	252214998	20260205	232037	전남87바1326	37.114520	127.027872	0	4.5	4.5	0	NOUSE	\N	37.11452	127.027872	2026-02-05 14:25:07.593217+00	\N
53	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-05 14:25:07.593217+00	\N
54	\N	0013668	252228119	20260205	232024	전남87바1336	35.814664	127.028472	0	4.0	4	0	NOUSE	\N	35.814664	127.028472	2026-02-05 14:25:07.593217+00	\N
55	\N	0013668	251512431	20260205	232429	전남87바1351	36.086938	127.105187	1	25.4	-25.4	0	NOUSE	\N	36.086938	127.105187	2026-02-05 14:25:07.593217+00	\N
56	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-05 14:25:07.593217+00	\N
57	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-05 14:25:07.593217+00	\N
58	\N	0013668	252227305	20260205	210311	전남87바1361	36.010416	126.798848	0	6.8	6.8	0	NOUSE	\N	36.010416	126.798848	2026-02-05 14:25:07.593217+00	\N
59	\N	0013668	236994200	20260205	125653	전남87바1362	37.087180	127.217069	0	2.6	2.6	0	6.2	6.2	37.08718	127.217069	2026-02-05 14:25:07.593217+00	\N
60	\N	0013668	252215001	20260205	225540	전남87바1364	37.114908	127.026848	0	4.0	4	0	NOUSE	\N	37.114908	127.026848	2026-02-05 14:25:07.593217+00	\N
61	\N	0013668	235771010	20260205	115249	전남87바1367	37.081004	127.207818	1	1.1	-1.1	0	NOUSE	\N	37.081004	127.207818	2026-02-05 14:25:07.593217+00	\N
62	\N	0013668	251512435	20260205	232104	전남87바1368	35.705813	126.755606	1	19.7	-19.7	0	NOUSE	\N	35.705813	126.755606	2026-02-05 14:25:07.593217+00	\N
63	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-05 14:25:07.593217+00	\N
64	\N	0013668	252227304	20260205	212612	전남87바1373	35.240496	127.023824	0	4.8	4.8	0	NOUSE	\N	35.240496	127.023824	2026-02-05 14:25:07.593217+00	\N
65	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-05 14:25:07.593217+00	\N
66	\N	0013668	235980831	20260205	232222	전남87바4156	35.104350	127.249368	1	19.9	-19.9	0	5.4	5.4	35.10435	127.249368	2026-02-05 14:25:07.593217+00	\N
67	\N	0013668	235994979	20260205	232404	전남87바4157	36.306972	127.308440	1	22.6	-22.6	0	NOUSE	\N	36.306972	127.30844	2026-02-05 14:25:07.593217+00	\N
68	\N	0013668	235771783	20260205	095250	전남87바4158	37.139846	127.395104	0	6.4	6.4	0	NOUSE	\N	37.139846	127.395104	2026-02-05 14:25:07.593217+00	\N
69	\N	0013668	252215000	20260205	232324	전남87바4159	35.751456	126.998984	1	17.7	-17.7	0	NOUSE	\N	35.751456	126.998984	2026-02-05 14:25:07.593217+00	\N
70	\N	0013668	252799355	20260203	233337	전남87바4161	35.248084	127.039168	0	2.5	2.5	0	NOUSE	\N	35.248084	127.039168	2026-02-05 14:25:07.593217+00	\N
71	\N	0013668	252227303	20260205	232222	전남87바4162	36.893756	127.189240	0	4.5	4.5	0	NOUSE	\N	36.893756	127.18924	2026-02-05 14:25:07.593217+00	\N
72	\N	0013668	251512429	20260205	232103	전남87바4165	35.348825	127.929377	1	20.3	-20.3	1	0.9	-0.9	35.348825	127.929377	2026-02-05 14:25:07.593217+00	\N
73	\N	0013668	236272742	20260130	173115	전남87바4166	36.006368	127.109768	0	4.5	4.5	0	7.7	7.7	36.006368	127.109768	2026-02-05 14:25:07.593217+00	\N
74	\N	0013668	252214993	20260204	223058	전남87바4169	35.247900	127.038832	0	3.2	3.2	0	NOUSE	\N	35.2479	127.038832	2026-02-05 14:25:07.593217+00	\N
75	\N	0013668	251509223	20260205	202326	전남87바4173	35.507608	128.782341	1	23.1	-23.1	0	NOUSE	\N	35.507608	128.782341	2026-02-05 14:25:07.593217+00	\N
76	\N	0013668	252228112	20260205	232012	전남87바4174	36.765408	127.984432	0	2.0	2	0	NOUSE	\N	36.765408	127.984432	2026-02-05 14:25:07.593217+00	\N
77	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-05 14:25:07.593217+00	\N
78	\N	0013668	252214992	20260205	203512	전남87바4176	35.876952	128.835176	0	2.0	2	0	NOUSE	\N	35.876952	128.835176	2026-02-05 14:25:07.593217+00	\N
79	\N	0013668	239200586	20260205	224946	전남87바4177	35.540326	127.310980	0	5.7	5.7	0	NOUSE	\N	35.540326	127.31098	2026-02-05 14:25:07.593217+00	\N
80	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-05 14:25:07.593217+00	\N
81	\N	0013668	240074478	20260205	201105	전남87바4188	35.248000	127.039472	1	22.8	-22.8	0	NOUSE	\N	35.248	127.039472	2026-02-05 14:25:07.593217+00	\N
82	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-05 14:25:07.593217+00	\N
83	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-05 14:30:07.681881+00	\N
84	\N	0013668	236275896	20260205	223326	전남87바1302	37.114276	127.027912	0	3.0	3	0	NOUSE	\N	37.114276	127.027912	2026-02-05 14:30:07.681881+00	\N
85	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-05 14:30:07.681881+00	\N
86	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-05 14:30:07.681881+00	\N
87	\N	0013668	252227307	20260205	225140	전남87바1305	35.373024	129.018192	1	14.6	-14.6	0	NOUSE	\N	35.373024	129.018192	2026-02-05 14:30:07.681881+00	\N
88	\N	0013668	252214997	20260205	223811	전남87바1313	35.147292	126.759000	0	2.6	2.6	0	NOUSE	\N	35.147292	126.759	2026-02-05 14:30:07.681881+00	\N
89	\N	0013668	252713338	20260205	232526	전남87바1317	35.434711	126.806328	1	22.2	-22.2	0	NOUSE	\N	35.434711	126.806328	2026-02-05 14:30:07.681881+00	\N
90	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-05 14:30:07.681881+00	\N
91	\N	0013668	252214999	20260205	232857	전남87바1320	35.269232	126.859352	0	1.3	1.3	0	NOUSE	\N	35.269232	126.859352	2026-02-05 14:30:07.681881+00	\N
92	\N	0013668	249253808	20260205	232742	전남87바1325	36.223036	126.778600	0	6.5	6.5	0	NOUSE	\N	36.223036	126.7786	2026-02-05 14:30:07.681881+00	\N
93	\N	0013668	252214998	20260205	232537	전남87바1326	37.114536	127.027880	0	4.5	4.5	0	NOUSE	\N	37.114536	127.02788	2026-02-05 14:30:07.681881+00	\N
94	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-05 14:30:07.681881+00	\N
95	\N	0013668	252228119	20260205	232524	전남87바1336	35.755868	126.999264	0	4.0	4	0	NOUSE	\N	35.755868	126.999264	2026-02-05 14:30:07.681881+00	\N
96	\N	0013668	251512431	20260205	232931	전남87바1351	36.029956	127.102949	1	26.2	-26.2	0	NOUSE	\N	36.029956	127.102949	2026-02-05 14:30:07.681881+00	\N
97	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-05 14:30:07.681881+00	\N
98	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-05 14:30:07.681881+00	\N
99	\N	0013668	252227305	20260205	210311	전남87바1361	36.010416	126.798848	0	6.8	6.8	0	NOUSE	\N	36.010416	126.798848	2026-02-05 14:30:07.681881+00	\N
100	\N	0013668	236994200	20260205	125653	전남87바1362	37.087180	127.217069	0	2.6	2.6	0	6.2	6.2	37.08718	127.217069	2026-02-05 14:30:07.681881+00	\N
101	\N	0013668	252215001	20260205	225540	전남87바1364	37.114908	127.026848	0	4.0	4	0	NOUSE	\N	37.114908	127.026848	2026-02-05 14:30:07.681881+00	\N
102	\N	0013668	235771010	20260205	115249	전남87바1367	37.081004	127.207818	1	1.1	-1.1	0	NOUSE	\N	37.081004	127.207818	2026-02-05 14:30:07.681881+00	\N
103	\N	0013668	251512435	20260205	232605	전남87바1368	35.648274	126.718779	1	21.5	-21.5	0	NOUSE	\N	35.648274	126.718779	2026-02-05 14:30:07.681881+00	\N
104	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-05 14:30:07.681881+00	\N
105	\N	0013668	252227304	20260205	212612	전남87바1373	35.240496	127.023824	0	4.8	4.8	0	NOUSE	\N	35.240496	127.023824	2026-02-05 14:30:07.681881+00	\N
106	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-05 14:30:07.681881+00	\N
107	\N	0013668	235980831	20260205	232725	전남87바4156	35.164437	127.252149	1	20.4	-20.4	0	5.4	5.4	35.164437	127.252149	2026-02-05 14:30:07.681881+00	\N
108	\N	0013668	235994979	20260205	232904	전남87바4157	36.263868	127.289320	1	22.8	-22.8	0	NOUSE	\N	36.263868	127.28932	2026-02-05 14:30:07.681881+00	\N
109	\N	0013668	235771783	20260205	095250	전남87바4158	37.139846	127.395104	0	6.4	6.4	0	NOUSE	\N	37.139846	127.395104	2026-02-05 14:30:07.681881+00	\N
110	\N	0013668	252215000	20260205	232824	전남87바4159	35.701604	126.958728	1	16.8	-16.8	0	NOUSE	\N	35.701604	126.958728	2026-02-05 14:30:07.681881+00	\N
111	\N	0013668	252799355	20260203	233337	전남87바4161	35.248084	127.039168	0	2.5	2.5	0	NOUSE	\N	35.248084	127.039168	2026-02-05 14:30:07.681881+00	\N
112	\N	0013668	252227303	20260205	232722	전남87바4162	36.957356	127.180560	0	4.5	4.5	0	NOUSE	\N	36.957356	127.18056	2026-02-05 14:30:07.681881+00	\N
113	\N	0013668	251512429	20260205	232605	전남87바4165	35.394234	127.889902	1	20.7	-20.7	1	0.8	-0.8	35.394234	127.889902	2026-02-05 14:30:07.681881+00	\N
114	\N	0013668	236272742	20260130	173115	전남87바4166	36.006368	127.109768	0	4.5	4.5	0	7.7	7.7	36.006368	127.109768	2026-02-05 14:30:07.681881+00	\N
115	\N	0013668	252214993	20260204	223058	전남87바4169	35.247900	127.038832	0	3.2	3.2	0	NOUSE	\N	35.2479	127.038832	2026-02-05 14:30:07.681881+00	\N
116	\N	0013668	251509223	20260205	202326	전남87바4173	35.507608	128.782341	1	23.1	-23.1	0	NOUSE	\N	35.507608	128.782341	2026-02-05 14:30:07.681881+00	\N
117	\N	0013668	252228112	20260205	232512	전남87바4174	0.000000	0.000000	0	2.0	2	0	NOUSE	\N	0	0	2026-02-05 14:30:07.681881+00	\N
118	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-05 14:30:07.681881+00	\N
119	\N	0013668	252214992	20260205	203512	전남87바4176	35.876952	128.835176	0	2.0	2	0	NOUSE	\N	35.876952	128.835176	2026-02-05 14:30:07.681881+00	\N
120	\N	0013668	239200586	20260205	224946	전남87바4177	35.540326	127.310980	0	5.7	5.7	0	NOUSE	\N	35.540326	127.31098	2026-02-05 14:30:07.681881+00	\N
121	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-05 14:30:07.681881+00	\N
122	\N	0013668	240074478	20260205	201105	전남87바4188	35.248000	127.039472	1	22.8	-22.8	0	NOUSE	\N	35.248	127.039472	2026-02-05 14:30:07.681881+00	\N
123	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-05 14:30:07.681881+00	\N
124	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 09:46:32.611617+00	\N
125	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 09:46:32.613105+00	\N
126	\N	0013668	236275896	20260206	184326	전남87바1302	0.000000	0.000000	0	1.9	1.9	0	NOUSE	\N	0	0	2026-02-06 09:46:32.611617+00	\N
127	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 09:46:32.611617+00	\N
128	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 09:46:32.611617+00	\N
129	\N	0013668	252227307	20260206	184245	전남87바1305	0.000000	0.000000	0	3.9	3.9	0	NOUSE	\N	0	0	2026-02-06 09:46:32.611617+00	\N
130	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 09:46:32.611617+00	\N
131	\N	0013668	252713338	20260206	184423	전남87바1317	36.140434	127.151039	0	2.6	2.6	0	NOUSE	\N	36.140434	127.151039	2026-02-06 09:46:32.611617+00	\N
132	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 09:46:32.611617+00	\N
133	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 09:46:32.611617+00	\N
134	\N	0013668	249253808	20260206	184242	전남87바1325	36.292124	127.317000	1	24.0	-24	0	NOUSE	\N	36.292124	127.317	2026-02-06 09:46:32.611617+00	\N
135	\N	0013668	252214998	20260206	180537	전남87바1326	35.290656	129.009640	1	22.3	-22.3	0	NOUSE	\N	35.290656	129.00964	2026-02-06 09:46:32.611617+00	\N
136	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 09:46:32.611617+00	\N
137	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 09:46:32.611617+00	\N
138	\N	0013668	251512431	20260206	184401	전남87바1351	37.248785	127.423621	1	19.8	-19.8	0	NOUSE	\N	37.248785	127.423621	2026-02-06 09:46:32.611617+00	\N
139	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 09:46:32.611617+00	\N
140	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 09:46:32.611617+00	\N
141	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 09:46:32.611617+00	\N
142	\N	0013668	236994200	20260206	184449	전남87바1362	36.670498	127.424291	0	1.6	1.6	0	2.8	2.8	36.670498	127.424291	2026-02-06 09:46:32.611617+00	\N
143	\N	0013668	252215001	20260206	184540	전남87바1364	36.976556	127.165016	0	3.1	3.1	0	NOUSE	\N	36.976556	127.165016	2026-02-06 09:46:32.611617+00	\N
144	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 09:46:32.611617+00	\N
145	\N	0013668	251512435	20260206	184138	전남87바1368	35.475282	128.774212	1	14.2	-14.2	0	1.9	1.9	35.475282	128.774212	2026-02-06 09:46:32.611617+00	\N
146	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 09:46:32.611617+00	\N
147	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 09:46:32.611617+00	\N
148	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 09:46:32.611617+00	\N
149	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 09:46:32.611617+00	\N
150	\N	0013668	235994979	20260206	184404	전남87바4157	35.112948	126.481280	0	5.4	5.4	0	NOUSE	\N	35.112948	126.48128	2026-02-06 09:46:32.611617+00	\N
151	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 09:46:32.611617+00	\N
152	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 09:46:32.611617+00	\N
153	\N	0013668	252799355	20260206	184442	전남87바4161	36.182004	128.262160	1	22.8	-22.8	0	NOUSE	\N	36.182004	128.26216	2026-02-06 09:46:32.611617+00	\N
154	\N	0013668	252227303	20260206	184222	전남87바4162	34.702736	126.663616	0	0.7	0.7	0	NOUSE	\N	34.702736	126.663616	2026-02-06 09:46:32.611617+00	\N
155	\N	0013668	251512429	20260206	184517	전남87바4165	37.264649	127.193204	1	21.4	-21.4	0	NOUSE	\N	37.264649	127.193204	2026-02-06 09:46:32.611617+00	\N
156	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 09:46:32.611617+00	\N
157	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 09:46:32.611617+00	\N
158	\N	0013668	251509223	20260206	184456	전남87바4173	0.000000	0.000000	1	21.8	-21.8	0	NOUSE	\N	0	0	2026-02-06 09:46:32.611617+00	\N
159	\N	0013668	252228112	20260206	184512	전남87바4174	35.263064	127.134520	1	25.3	-25.3	0	NOUSE	\N	35.263064	127.13452	2026-02-06 09:46:32.611617+00	\N
160	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 09:46:32.611617+00	\N
161	\N	0013668	252214992	20260206	184512	전남87바4176	35.054628	127.933808	0	3.0	3	0	NOUSE	\N	35.054628	127.933808	2026-02-06 09:46:32.611617+00	\N
162	\N	0013668	239200586	20260206	184325	전남87바4177	36.063729	128.737829	0	5.4	5.4	0	NOUSE	\N	36.063729	128.737829	2026-02-06 09:46:32.611617+00	\N
163	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 09:46:32.611617+00	\N
164	\N	0013668	240074478	20260206	184105	전남87바4188	36.257980	127.281160	1	22.4	-22.4	0	NOUSE	\N	36.25798	127.28116	2026-02-06 09:46:32.611617+00	\N
165	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 09:46:32.611617+00	\N
1313	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:52:02.909905+00	\N
1314	\N	0013668	236275896	20260206	194826	전남87바1302	35.168472	126.781480	0	1.3	1.3	0	NOUSE	\N	35.168472	126.78148	2026-02-06 10:52:02.909905+00	\N
1315	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:52:02.909905+00	\N
1316	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:52:02.909905+00	\N
1317	\N	0013668	252227307	20260206	194745	전남87바1305	35.530112	129.107760	0	2.8	2.8	0	NOUSE	\N	35.530112	129.10776	2026-02-06 10:52:02.909905+00	\N
1318	\N	0013668	252214997	20260206	194916	전남87바1313	37.266500	127.499336	1	18.6	-18.6	0	NOUSE	\N	37.2665	127.499336	2026-02-06 10:52:02.909905+00	\N
1319	\N	0013668	252713338	20260206	194948	전남87바1317	36.687862	127.425547	0	2.7	2.7	0	NOUSE	\N	36.687862	127.425547	2026-02-06 10:52:02.909905+00	\N
1320	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:52:02.909905+00	\N
1321	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:52:02.909905+00	\N
1322	\N	0013668	249253808	20260206	194742	전남87바1325	36.984048	127.471768	1	20.4	-20.4	0	NOUSE	\N	36.984048	127.471768	2026-02-06 10:52:02.909905+00	\N
1323	\N	0013668	252214998	20260206	195037	전남87바1326	35.273656	128.973832	1	19.8	-19.8	1	1.3	-1.3	35.273656	128.973832	2026-02-06 10:52:02.909905+00	\N
1324	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:52:02.909905+00	\N
1325	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:52:02.909905+00	\N
1326	\N	0013668	251512431	20260206	190910	전남87바1351	37.248838	127.423753	1	25.1	-25.1	0	NOUSE	\N	37.248838	127.423753	2026-02-06 10:52:02.909905+00	\N
1327	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:52:02.909905+00	\N
1328	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:52:02.909905+00	\N
1329	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:52:02.909905+00	\N
1330	\N	0013668	236994200	20260206	195013	전남87바1362	36.085836	127.104505	0	1.8	1.8	0	2.9	2.9	36.085836	127.104505	2026-02-06 10:52:02.909905+00	\N
1331	\N	0013668	252215001	20260206	191540	전남87바1364	37.087188	127.216976	0	3.7	3.7	0	NOUSE	\N	37.087188	127.216976	2026-02-06 10:52:02.909905+00	\N
1332	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:52:02.909905+00	\N
1333	\N	0013668	251512435	20260206	194914	전남87바1368	35.258302	128.825201	1	18.8	-18.8	0	5.0	5	35.258302	128.825201	2026-02-06 10:52:02.909905+00	\N
1334	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:52:02.909905+00	\N
1335	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:52:02.909905+00	\N
166	\N	0013668	236275896	20260206	184326	전남87바1302	0.000000	0.000000	0	1.9	1.9	0	NOUSE	\N	0	0	2026-02-06 09:46:32.613105+00	\N
167	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 09:46:32.613105+00	\N
168	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 09:46:32.613105+00	\N
169	\N	0013668	252227307	20260206	184245	전남87바1305	0.000000	0.000000	0	3.9	3.9	0	NOUSE	\N	0	0	2026-02-06 09:46:32.613105+00	\N
170	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 09:46:32.613105+00	\N
171	\N	0013668	252713338	20260206	184423	전남87바1317	36.140434	127.151039	0	2.6	2.6	0	NOUSE	\N	36.140434	127.151039	2026-02-06 09:46:32.613105+00	\N
172	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 09:46:32.613105+00	\N
173	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 09:46:32.613105+00	\N
174	\N	0013668	249253808	20260206	184242	전남87바1325	36.292124	127.317000	1	24.0	-24	0	NOUSE	\N	36.292124	127.317	2026-02-06 09:46:32.613105+00	\N
175	\N	0013668	252214998	20260206	180537	전남87바1326	35.290656	129.009640	1	22.3	-22.3	0	NOUSE	\N	35.290656	129.00964	2026-02-06 09:46:32.613105+00	\N
176	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 09:46:32.613105+00	\N
177	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 09:46:32.613105+00	\N
178	\N	0013668	251512431	20260206	184401	전남87바1351	37.248785	127.423621	1	19.8	-19.8	0	NOUSE	\N	37.248785	127.423621	2026-02-06 09:46:32.613105+00	\N
179	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 09:46:32.613105+00	\N
180	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 09:46:32.613105+00	\N
181	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 09:46:32.613105+00	\N
182	\N	0013668	236994200	20260206	184449	전남87바1362	36.670498	127.424291	0	1.6	1.6	0	2.8	2.8	36.670498	127.424291	2026-02-06 09:46:32.613105+00	\N
183	\N	0013668	252215001	20260206	184540	전남87바1364	36.976556	127.165016	0	3.1	3.1	0	NOUSE	\N	36.976556	127.165016	2026-02-06 09:46:32.613105+00	\N
184	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 09:46:32.613105+00	\N
185	\N	0013668	251512435	20260206	184138	전남87바1368	35.475282	128.774212	1	14.2	-14.2	0	1.9	1.9	35.475282	128.774212	2026-02-06 09:46:32.613105+00	\N
186	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 09:46:32.613105+00	\N
187	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 09:46:32.613105+00	\N
188	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 09:46:32.613105+00	\N
189	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 09:46:32.613105+00	\N
190	\N	0013668	235994979	20260206	184404	전남87바4157	35.112948	126.481280	0	5.4	5.4	0	NOUSE	\N	35.112948	126.48128	2026-02-06 09:46:32.613105+00	\N
191	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 09:46:32.613105+00	\N
192	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 09:46:32.613105+00	\N
193	\N	0013668	252799355	20260206	184442	전남87바4161	36.182004	128.262160	1	22.8	-22.8	0	NOUSE	\N	36.182004	128.26216	2026-02-06 09:46:32.613105+00	\N
194	\N	0013668	252227303	20260206	184222	전남87바4162	34.702736	126.663616	0	0.7	0.7	0	NOUSE	\N	34.702736	126.663616	2026-02-06 09:46:32.613105+00	\N
195	\N	0013668	251512429	20260206	184517	전남87바4165	37.264649	127.193204	1	21.4	-21.4	0	NOUSE	\N	37.264649	127.193204	2026-02-06 09:46:32.613105+00	\N
196	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 09:46:32.613105+00	\N
197	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 09:46:32.613105+00	\N
198	\N	0013668	251509223	20260206	184456	전남87바4173	0.000000	0.000000	1	21.8	-21.8	0	NOUSE	\N	0	0	2026-02-06 09:46:32.613105+00	\N
199	\N	0013668	252228112	20260206	184512	전남87바4174	35.263064	127.134520	1	25.3	-25.3	0	NOUSE	\N	35.263064	127.13452	2026-02-06 09:46:32.613105+00	\N
200	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 09:46:32.613105+00	\N
201	\N	0013668	252214992	20260206	184512	전남87바4176	35.054628	127.933808	0	3.0	3	0	NOUSE	\N	35.054628	127.933808	2026-02-06 09:46:32.613105+00	\N
202	\N	0013668	239200586	20260206	184325	전남87바4177	36.063729	128.737829	0	5.4	5.4	0	NOUSE	\N	36.063729	128.737829	2026-02-06 09:46:32.613105+00	\N
203	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 09:46:32.613105+00	\N
204	\N	0013668	240074478	20260206	184105	전남87바4188	36.257980	127.281160	1	22.4	-22.4	0	NOUSE	\N	36.25798	127.28116	2026-02-06 09:46:32.613105+00	\N
205	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 09:46:32.613105+00	\N
206	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 09:46:32.66325+00	\N
207	\N	0013668	236275896	20260206	184326	전남87바1302	0.000000	0.000000	0	1.9	1.9	0	NOUSE	\N	0	0	2026-02-06 09:46:32.66325+00	\N
208	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 09:46:32.66325+00	\N
209	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 09:46:32.66325+00	\N
210	\N	0013668	252227307	20260206	184245	전남87바1305	0.000000	0.000000	0	3.9	3.9	0	NOUSE	\N	0	0	2026-02-06 09:46:32.66325+00	\N
211	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 09:46:32.66325+00	\N
212	\N	0013668	252713338	20260206	184423	전남87바1317	36.140434	127.151039	0	2.6	2.6	0	NOUSE	\N	36.140434	127.151039	2026-02-06 09:46:32.66325+00	\N
213	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 09:46:32.66325+00	\N
214	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 09:46:32.66325+00	\N
215	\N	0013668	249253808	20260206	184242	전남87바1325	36.292124	127.317000	1	24.0	-24	0	NOUSE	\N	36.292124	127.317	2026-02-06 09:46:32.66325+00	\N
216	\N	0013668	252214998	20260206	180537	전남87바1326	35.290656	129.009640	1	22.3	-22.3	0	NOUSE	\N	35.290656	129.00964	2026-02-06 09:46:32.66325+00	\N
217	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 09:46:32.66325+00	\N
218	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 09:46:32.66325+00	\N
219	\N	0013668	251512431	20260206	184401	전남87바1351	37.248785	127.423621	1	19.8	-19.8	0	NOUSE	\N	37.248785	127.423621	2026-02-06 09:46:32.66325+00	\N
220	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 09:46:32.66325+00	\N
221	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 09:46:32.66325+00	\N
222	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 09:46:32.66325+00	\N
223	\N	0013668	236994200	20260206	184449	전남87바1362	36.670498	127.424291	0	1.6	1.6	0	2.8	2.8	36.670498	127.424291	2026-02-06 09:46:32.66325+00	\N
224	\N	0013668	252215001	20260206	184540	전남87바1364	36.976556	127.165016	0	3.1	3.1	0	NOUSE	\N	36.976556	127.165016	2026-02-06 09:46:32.66325+00	\N
225	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 09:46:32.66325+00	\N
226	\N	0013668	251512435	20260206	184138	전남87바1368	35.475282	128.774212	1	14.2	-14.2	0	1.9	1.9	35.475282	128.774212	2026-02-06 09:46:32.66325+00	\N
227	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 09:46:32.66325+00	\N
228	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 09:46:32.66325+00	\N
229	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 09:46:32.66325+00	\N
230	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 09:46:32.66325+00	\N
231	\N	0013668	235994979	20260206	184404	전남87바4157	35.112948	126.481280	0	5.4	5.4	0	NOUSE	\N	35.112948	126.48128	2026-02-06 09:46:32.66325+00	\N
232	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 09:46:32.66325+00	\N
233	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 09:46:32.66325+00	\N
234	\N	0013668	252799355	20260206	184442	전남87바4161	36.182004	128.262160	1	22.8	-22.8	0	NOUSE	\N	36.182004	128.26216	2026-02-06 09:46:32.66325+00	\N
235	\N	0013668	252227303	20260206	184222	전남87바4162	34.702736	126.663616	0	0.7	0.7	0	NOUSE	\N	34.702736	126.663616	2026-02-06 09:46:32.66325+00	\N
236	\N	0013668	251512429	20260206	184517	전남87바4165	37.264649	127.193204	1	21.4	-21.4	0	NOUSE	\N	37.264649	127.193204	2026-02-06 09:46:32.66325+00	\N
237	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 09:46:32.66325+00	\N
238	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 09:46:32.66325+00	\N
239	\N	0013668	251509223	20260206	184456	전남87바4173	0.000000	0.000000	1	21.8	-21.8	0	NOUSE	\N	0	0	2026-02-06 09:46:32.66325+00	\N
240	\N	0013668	252228112	20260206	184512	전남87바4174	35.263064	127.134520	1	25.3	-25.3	0	NOUSE	\N	35.263064	127.13452	2026-02-06 09:46:32.66325+00	\N
241	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 09:46:32.66325+00	\N
242	\N	0013668	252214992	20260206	184512	전남87바4176	35.054628	127.933808	0	3.0	3	0	NOUSE	\N	35.054628	127.933808	2026-02-06 09:46:32.66325+00	\N
243	\N	0013668	239200586	20260206	184325	전남87바4177	36.063729	128.737829	0	5.4	5.4	0	NOUSE	\N	36.063729	128.737829	2026-02-06 09:46:32.66325+00	\N
244	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 09:46:32.66325+00	\N
245	\N	0013668	240074478	20260206	184105	전남87바4188	36.257980	127.281160	1	22.4	-22.4	0	NOUSE	\N	36.25798	127.28116	2026-02-06 09:46:32.66325+00	\N
246	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 09:46:32.66325+00	\N
247	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 09:46:34.452057+00	\N
248	\N	0013668	236275896	20260206	184326	전남87바1302	0.000000	0.000000	0	1.9	1.9	0	NOUSE	\N	0	0	2026-02-06 09:46:34.452057+00	\N
249	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 09:46:34.452057+00	\N
250	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 09:46:34.452057+00	\N
251	\N	0013668	252227307	20260206	184245	전남87바1305	0.000000	0.000000	0	3.9	3.9	0	NOUSE	\N	0	0	2026-02-06 09:46:34.452057+00	\N
252	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 09:46:34.452057+00	\N
253	\N	0013668	252713338	20260206	184423	전남87바1317	36.140434	127.151039	0	2.6	2.6	0	NOUSE	\N	36.140434	127.151039	2026-02-06 09:46:34.452057+00	\N
254	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 09:46:34.452057+00	\N
255	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 09:46:34.452057+00	\N
256	\N	0013668	249253808	20260206	184242	전남87바1325	36.292124	127.317000	1	24.0	-24	0	NOUSE	\N	36.292124	127.317	2026-02-06 09:46:34.452057+00	\N
257	\N	0013668	252214998	20260206	180537	전남87바1326	35.290656	129.009640	1	22.3	-22.3	0	NOUSE	\N	35.290656	129.00964	2026-02-06 09:46:34.452057+00	\N
258	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 09:46:34.452057+00	\N
259	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 09:46:34.452057+00	\N
260	\N	0013668	251512431	20260206	184401	전남87바1351	37.248785	127.423621	1	19.8	-19.8	0	NOUSE	\N	37.248785	127.423621	2026-02-06 09:46:34.452057+00	\N
261	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 09:46:34.452057+00	\N
262	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 09:46:34.452057+00	\N
263	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 09:46:34.452057+00	\N
264	\N	0013668	236994200	20260206	184449	전남87바1362	36.670498	127.424291	0	1.6	1.6	0	2.8	2.8	36.670498	127.424291	2026-02-06 09:46:34.452057+00	\N
265	\N	0013668	252215001	20260206	184540	전남87바1364	36.976556	127.165016	0	3.1	3.1	0	NOUSE	\N	36.976556	127.165016	2026-02-06 09:46:34.452057+00	\N
266	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 09:46:34.452057+00	\N
267	\N	0013668	251512435	20260206	184138	전남87바1368	35.475282	128.774212	1	14.2	-14.2	0	1.9	1.9	35.475282	128.774212	2026-02-06 09:46:34.452057+00	\N
268	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 09:46:34.452057+00	\N
269	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 09:46:34.452057+00	\N
270	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 09:46:34.452057+00	\N
271	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 09:46:34.452057+00	\N
272	\N	0013668	235994979	20260206	184404	전남87바4157	35.112948	126.481280	0	5.4	5.4	0	NOUSE	\N	35.112948	126.48128	2026-02-06 09:46:34.452057+00	\N
273	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 09:46:34.452057+00	\N
274	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 09:46:34.452057+00	\N
275	\N	0013668	252799355	20260206	184442	전남87바4161	36.182004	128.262160	1	22.8	-22.8	0	NOUSE	\N	36.182004	128.26216	2026-02-06 09:46:34.452057+00	\N
276	\N	0013668	252227303	20260206	184222	전남87바4162	34.702736	126.663616	0	0.7	0.7	0	NOUSE	\N	34.702736	126.663616	2026-02-06 09:46:34.452057+00	\N
277	\N	0013668	251512429	20260206	184517	전남87바4165	37.264649	127.193204	1	21.4	-21.4	0	NOUSE	\N	37.264649	127.193204	2026-02-06 09:46:34.452057+00	\N
278	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 09:46:34.452057+00	\N
279	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 09:46:34.452057+00	\N
280	\N	0013668	251509223	20260206	184456	전남87바4173	0.000000	0.000000	1	21.8	-21.8	0	NOUSE	\N	0	0	2026-02-06 09:46:34.452057+00	\N
281	\N	0013668	252228112	20260206	184512	전남87바4174	35.263064	127.134520	1	25.3	-25.3	0	NOUSE	\N	35.263064	127.13452	2026-02-06 09:46:34.452057+00	\N
282	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 09:46:34.452057+00	\N
283	\N	0013668	252214992	20260206	184512	전남87바4176	35.054628	127.933808	0	3.0	3	0	NOUSE	\N	35.054628	127.933808	2026-02-06 09:46:34.452057+00	\N
284	\N	0013668	239200586	20260206	184325	전남87바4177	36.063729	128.737829	0	5.4	5.4	0	NOUSE	\N	36.063729	128.737829	2026-02-06 09:46:34.452057+00	\N
285	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 09:46:34.452057+00	\N
286	\N	0013668	240074478	20260206	184105	전남87바4188	36.257980	127.281160	1	22.4	-22.4	0	NOUSE	\N	36.25798	127.28116	2026-02-06 09:46:34.452057+00	\N
287	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 09:46:34.452057+00	\N
288	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 09:51:32.528049+00	\N
289	\N	0013668	236275896	20260206	184826	전남87바1302	0.000000	0.000000	0	1.9	1.9	0	NOUSE	\N	0	0	2026-02-06 09:51:32.528049+00	\N
290	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 09:51:32.528049+00	\N
291	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 09:51:32.528049+00	\N
292	\N	0013668	252227307	20260206	184745	전남87바1305	35.278152	128.985184	0	4.0	4	0	NOUSE	\N	35.278152	128.985184	2026-02-06 09:51:32.528049+00	\N
293	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 09:51:32.528049+00	\N
294	\N	0013668	252713338	20260206	184925	전남87바1317	36.159012	127.209445	0	2.5	2.5	0	NOUSE	\N	36.159012	127.209445	2026-02-06 09:51:32.528049+00	\N
295	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 09:51:32.528049+00	\N
296	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 09:51:32.528049+00	\N
297	\N	0013668	249253808	20260206	184742	전남87바1325	36.351412	127.325088	1	19.9	-19.9	0	NOUSE	\N	36.351412	127.325088	2026-02-06 09:51:32.528049+00	\N
298	\N	0013668	252214998	20260206	180537	전남87바1326	35.290656	129.009640	1	22.3	-22.3	0	NOUSE	\N	35.290656	129.00964	2026-02-06 09:51:32.528049+00	\N
299	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 09:51:32.528049+00	\N
300	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 09:51:32.528049+00	\N
301	\N	0013668	251512431	20260206	184903	전남87바1351	37.248778	127.423619	1	20.9	-20.9	0	NOUSE	\N	37.248778	127.423619	2026-02-06 09:51:32.528049+00	\N
302	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 09:51:32.528049+00	\N
303	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 09:51:32.528049+00	\N
304	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 09:51:32.528049+00	\N
305	\N	0013668	236994200	20260206	184951	전남87바1362	36.621507	127.420100	0	1.5	1.5	0	2.9	2.9	36.621507	127.4201	2026-02-06 09:51:32.528049+00	\N
306	\N	0013668	252215001	20260206	185040	전남87바1364	36.997672	127.153104	0	3.4	3.4	0	NOUSE	\N	36.997672	127.153104	2026-02-06 09:51:32.528049+00	\N
307	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 09:51:32.528049+00	\N
308	\N	0013668	251512435	20260206	184639	전남87바1368	35.414313	128.794972	1	19.5	-19.5	0	1.1	1.1	35.414313	128.794972	2026-02-06 09:51:32.528049+00	\N
309	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 09:51:32.528049+00	\N
310	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 09:51:32.528049+00	\N
311	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 09:51:32.528049+00	\N
312	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 09:51:32.528049+00	\N
313	\N	0013668	235994979	20260206	184904	전남87바4157	35.178884	126.483000	0	5.4	5.4	0	NOUSE	\N	35.178884	126.483	2026-02-06 09:51:32.528049+00	\N
314	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 09:51:32.528049+00	\N
315	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 09:51:32.528049+00	\N
316	\N	0013668	252799355	20260206	184942	전남87바4161	36.144376	128.298480	1	19.8	-19.8	0	NOUSE	\N	36.144376	128.29848	2026-02-06 09:51:32.528049+00	\N
317	\N	0013668	252227303	20260206	184722	전남87바4162	34.729060	126.596072	0	1.1	1.1	0	NOUSE	\N	34.72906	126.596072	2026-02-06 09:51:32.528049+00	\N
318	\N	0013668	251512429	20260206	185019	전남87바4165	37.246338	127.267346	1	23.1	-23.1	0	NOUSE	\N	37.246338	127.267346	2026-02-06 09:51:32.528049+00	\N
319	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 09:51:32.528049+00	\N
320	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 09:51:32.528049+00	\N
321	\N	0013668	251509223	20260206	184958	전남87바4173	36.684817	128.119248	1	23.1	-23.1	0	NOUSE	\N	36.684817	128.119248	2026-02-06 09:51:32.528049+00	\N
322	\N	0013668	252228112	20260206	185012	전남87바4174	35.258640	127.061000	1	22.3	-22.3	0	NOUSE	\N	35.25864	127.061	2026-02-06 09:51:32.528049+00	\N
323	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 09:51:32.528049+00	\N
324	\N	0013668	252214992	20260206	185012	전남87바4176	35.028824	127.868264	0	3.0	3	0	NOUSE	\N	35.028824	127.868264	2026-02-06 09:51:32.528049+00	\N
325	\N	0013668	239200586	20260206	184828	전남87바4177	36.094525	128.664688	0	5.7	5.7	0	NOUSE	\N	36.094525	128.664688	2026-02-06 09:51:32.528049+00	\N
326	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 09:51:32.528049+00	\N
327	\N	0013668	240074478	20260206	184605	전남87바4188	36.203784	127.266080	1	21.9	-21.9	0	NOUSE	\N	36.203784	127.26608	2026-02-06 09:51:32.528049+00	\N
328	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 09:51:32.528049+00	\N
329	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 09:51:32.529371+00	\N
330	\N	0013668	236275896	20260206	184826	전남87바1302	0.000000	0.000000	0	1.9	1.9	0	NOUSE	\N	0	0	2026-02-06 09:51:32.529371+00	\N
331	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 09:51:32.529371+00	\N
332	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 09:51:32.529371+00	\N
333	\N	0013668	252227307	20260206	184745	전남87바1305	35.278152	128.985184	0	4.0	4	0	NOUSE	\N	35.278152	128.985184	2026-02-06 09:51:32.529371+00	\N
334	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 09:51:32.529371+00	\N
335	\N	0013668	252713338	20260206	184925	전남87바1317	36.159012	127.209445	0	2.5	2.5	0	NOUSE	\N	36.159012	127.209445	2026-02-06 09:51:32.529371+00	\N
336	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 09:51:32.529371+00	\N
337	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 09:51:32.529371+00	\N
338	\N	0013668	249253808	20260206	184742	전남87바1325	36.351412	127.325088	1	19.9	-19.9	0	NOUSE	\N	36.351412	127.325088	2026-02-06 09:51:32.529371+00	\N
339	\N	0013668	252214998	20260206	180537	전남87바1326	35.290656	129.009640	1	22.3	-22.3	0	NOUSE	\N	35.290656	129.00964	2026-02-06 09:51:32.529371+00	\N
340	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 09:51:32.529371+00	\N
341	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 09:51:32.529371+00	\N
342	\N	0013668	251512431	20260206	184903	전남87바1351	37.248778	127.423619	1	20.9	-20.9	0	NOUSE	\N	37.248778	127.423619	2026-02-06 09:51:32.529371+00	\N
343	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 09:51:32.529371+00	\N
344	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 09:51:32.529371+00	\N
345	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 09:51:32.529371+00	\N
346	\N	0013668	236994200	20260206	184951	전남87바1362	36.621507	127.420100	0	1.5	1.5	0	2.9	2.9	36.621507	127.4201	2026-02-06 09:51:32.529371+00	\N
347	\N	0013668	252215001	20260206	185040	전남87바1364	36.997672	127.153104	0	3.4	3.4	0	NOUSE	\N	36.997672	127.153104	2026-02-06 09:51:32.529371+00	\N
348	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 09:51:32.529371+00	\N
349	\N	0013668	251512435	20260206	184639	전남87바1368	35.414313	128.794972	1	19.5	-19.5	0	1.1	1.1	35.414313	128.794972	2026-02-06 09:51:32.529371+00	\N
350	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 09:51:32.529371+00	\N
351	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 09:51:32.529371+00	\N
352	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 09:51:32.529371+00	\N
353	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 09:51:32.529371+00	\N
354	\N	0013668	235994979	20260206	184904	전남87바4157	35.178884	126.483000	0	5.4	5.4	0	NOUSE	\N	35.178884	126.483	2026-02-06 09:51:32.529371+00	\N
355	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 09:51:32.529371+00	\N
356	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 09:51:32.529371+00	\N
357	\N	0013668	252799355	20260206	184942	전남87바4161	36.144376	128.298480	1	19.8	-19.8	0	NOUSE	\N	36.144376	128.29848	2026-02-06 09:51:32.529371+00	\N
358	\N	0013668	252227303	20260206	184722	전남87바4162	34.729060	126.596072	0	1.1	1.1	0	NOUSE	\N	34.72906	126.596072	2026-02-06 09:51:32.529371+00	\N
359	\N	0013668	251512429	20260206	185019	전남87바4165	37.246338	127.267346	1	23.1	-23.1	0	NOUSE	\N	37.246338	127.267346	2026-02-06 09:51:32.529371+00	\N
360	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 09:51:32.529371+00	\N
361	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 09:51:32.529371+00	\N
362	\N	0013668	251509223	20260206	184958	전남87바4173	36.684817	128.119248	1	23.1	-23.1	0	NOUSE	\N	36.684817	128.119248	2026-02-06 09:51:32.529371+00	\N
363	\N	0013668	252228112	20260206	185012	전남87바4174	35.258640	127.061000	1	22.3	-22.3	0	NOUSE	\N	35.25864	127.061	2026-02-06 09:51:32.529371+00	\N
364	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 09:51:32.529371+00	\N
365	\N	0013668	252214992	20260206	185012	전남87바4176	35.028824	127.868264	0	3.0	3	0	NOUSE	\N	35.028824	127.868264	2026-02-06 09:51:32.529371+00	\N
366	\N	0013668	239200586	20260206	184828	전남87바4177	36.094525	128.664688	0	5.7	5.7	0	NOUSE	\N	36.094525	128.664688	2026-02-06 09:51:32.529371+00	\N
367	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 09:51:32.529371+00	\N
368	\N	0013668	240074478	20260206	184605	전남87바4188	36.203784	127.266080	1	21.9	-21.9	0	NOUSE	\N	36.203784	127.26608	2026-02-06 09:51:32.529371+00	\N
369	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 09:51:32.529371+00	\N
370	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 09:51:32.5294+00	\N
371	\N	0013668	236275896	20260206	184826	전남87바1302	0.000000	0.000000	0	1.9	1.9	0	NOUSE	\N	0	0	2026-02-06 09:51:32.5294+00	\N
372	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 09:51:32.5294+00	\N
373	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 09:51:32.5294+00	\N
374	\N	0013668	252227307	20260206	184745	전남87바1305	35.278152	128.985184	0	4.0	4	0	NOUSE	\N	35.278152	128.985184	2026-02-06 09:51:32.5294+00	\N
375	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 09:51:32.5294+00	\N
376	\N	0013668	252713338	20260206	184925	전남87바1317	36.159012	127.209445	0	2.5	2.5	0	NOUSE	\N	36.159012	127.209445	2026-02-06 09:51:32.5294+00	\N
377	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 09:51:32.5294+00	\N
378	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 09:51:32.5294+00	\N
379	\N	0013668	249253808	20260206	184742	전남87바1325	36.351412	127.325088	1	19.9	-19.9	0	NOUSE	\N	36.351412	127.325088	2026-02-06 09:51:32.5294+00	\N
380	\N	0013668	252214998	20260206	180537	전남87바1326	35.290656	129.009640	1	22.3	-22.3	0	NOUSE	\N	35.290656	129.00964	2026-02-06 09:51:32.5294+00	\N
381	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 09:51:32.5294+00	\N
382	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 09:51:32.5294+00	\N
383	\N	0013668	251512431	20260206	184903	전남87바1351	37.248778	127.423619	1	20.9	-20.9	0	NOUSE	\N	37.248778	127.423619	2026-02-06 09:51:32.5294+00	\N
384	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 09:51:32.5294+00	\N
385	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 09:51:32.5294+00	\N
386	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 09:51:32.5294+00	\N
387	\N	0013668	236994200	20260206	184951	전남87바1362	36.621507	127.420100	0	1.5	1.5	0	2.9	2.9	36.621507	127.4201	2026-02-06 09:51:32.5294+00	\N
388	\N	0013668	252215001	20260206	185040	전남87바1364	36.997672	127.153104	0	3.4	3.4	0	NOUSE	\N	36.997672	127.153104	2026-02-06 09:51:32.5294+00	\N
389	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 09:51:32.5294+00	\N
390	\N	0013668	251512435	20260206	184639	전남87바1368	35.414313	128.794972	1	19.5	-19.5	0	1.1	1.1	35.414313	128.794972	2026-02-06 09:51:32.5294+00	\N
391	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 09:51:32.5294+00	\N
392	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 09:51:32.5294+00	\N
393	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 09:51:32.5294+00	\N
394	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 09:51:32.5294+00	\N
395	\N	0013668	235994979	20260206	184904	전남87바4157	35.178884	126.483000	0	5.4	5.4	0	NOUSE	\N	35.178884	126.483	2026-02-06 09:51:32.5294+00	\N
396	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 09:51:32.5294+00	\N
397	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 09:51:32.5294+00	\N
398	\N	0013668	252799355	20260206	184942	전남87바4161	36.144376	128.298480	1	19.8	-19.8	0	NOUSE	\N	36.144376	128.29848	2026-02-06 09:51:32.5294+00	\N
399	\N	0013668	252227303	20260206	184722	전남87바4162	34.729060	126.596072	0	1.1	1.1	0	NOUSE	\N	34.72906	126.596072	2026-02-06 09:51:32.5294+00	\N
400	\N	0013668	251512429	20260206	185019	전남87바4165	37.246338	127.267346	1	23.1	-23.1	0	NOUSE	\N	37.246338	127.267346	2026-02-06 09:51:32.5294+00	\N
401	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 09:51:32.5294+00	\N
402	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 09:51:32.5294+00	\N
403	\N	0013668	251509223	20260206	184958	전남87바4173	36.684817	128.119248	1	23.1	-23.1	0	NOUSE	\N	36.684817	128.119248	2026-02-06 09:51:32.5294+00	\N
404	\N	0013668	252228112	20260206	185012	전남87바4174	35.258640	127.061000	1	22.3	-22.3	0	NOUSE	\N	35.25864	127.061	2026-02-06 09:51:32.5294+00	\N
405	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 09:51:32.5294+00	\N
406	\N	0013668	252214992	20260206	185012	전남87바4176	35.028824	127.868264	0	3.0	3	0	NOUSE	\N	35.028824	127.868264	2026-02-06 09:51:32.5294+00	\N
407	\N	0013668	239200586	20260206	184828	전남87바4177	36.094525	128.664688	0	5.7	5.7	0	NOUSE	\N	36.094525	128.664688	2026-02-06 09:51:32.5294+00	\N
408	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 09:51:32.5294+00	\N
409	\N	0013668	240074478	20260206	184605	전남87바4188	36.203784	127.266080	1	21.9	-21.9	0	NOUSE	\N	36.203784	127.26608	2026-02-06 09:51:32.5294+00	\N
410	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 09:51:32.5294+00	\N
411	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 09:51:32.529806+00	\N
412	\N	0013668	236275896	20260206	184826	전남87바1302	0.000000	0.000000	0	1.9	1.9	0	NOUSE	\N	0	0	2026-02-06 09:51:32.529806+00	\N
413	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 09:51:32.529806+00	\N
414	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 09:51:32.529806+00	\N
415	\N	0013668	252227307	20260206	184745	전남87바1305	35.278152	128.985184	0	4.0	4	0	NOUSE	\N	35.278152	128.985184	2026-02-06 09:51:32.529806+00	\N
416	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 09:51:32.529806+00	\N
417	\N	0013668	252713338	20260206	184925	전남87바1317	36.159012	127.209445	0	2.5	2.5	0	NOUSE	\N	36.159012	127.209445	2026-02-06 09:51:32.529806+00	\N
418	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 09:51:32.529806+00	\N
419	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 09:51:32.529806+00	\N
420	\N	0013668	249253808	20260206	184742	전남87바1325	36.351412	127.325088	1	19.9	-19.9	0	NOUSE	\N	36.351412	127.325088	2026-02-06 09:51:32.529806+00	\N
421	\N	0013668	252214998	20260206	180537	전남87바1326	35.290656	129.009640	1	22.3	-22.3	0	NOUSE	\N	35.290656	129.00964	2026-02-06 09:51:32.529806+00	\N
422	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 09:51:32.529806+00	\N
423	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 09:51:32.529806+00	\N
424	\N	0013668	251512431	20260206	184903	전남87바1351	37.248778	127.423619	1	20.9	-20.9	0	NOUSE	\N	37.248778	127.423619	2026-02-06 09:51:32.529806+00	\N
425	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 09:51:32.529806+00	\N
426	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 09:51:32.529806+00	\N
427	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 09:51:32.529806+00	\N
428	\N	0013668	236994200	20260206	184951	전남87바1362	36.621507	127.420100	0	1.5	1.5	0	2.9	2.9	36.621507	127.4201	2026-02-06 09:51:32.529806+00	\N
429	\N	0013668	252215001	20260206	185040	전남87바1364	36.997672	127.153104	0	3.4	3.4	0	NOUSE	\N	36.997672	127.153104	2026-02-06 09:51:32.529806+00	\N
430	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 09:51:32.529806+00	\N
431	\N	0013668	251512435	20260206	184639	전남87바1368	35.414313	128.794972	1	19.5	-19.5	0	1.1	1.1	35.414313	128.794972	2026-02-06 09:51:32.529806+00	\N
432	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 09:51:32.529806+00	\N
433	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 09:51:32.529806+00	\N
434	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 09:51:32.529806+00	\N
435	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 09:51:32.529806+00	\N
436	\N	0013668	235994979	20260206	184904	전남87바4157	35.178884	126.483000	0	5.4	5.4	0	NOUSE	\N	35.178884	126.483	2026-02-06 09:51:32.529806+00	\N
437	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 09:51:32.529806+00	\N
438	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 09:51:32.529806+00	\N
439	\N	0013668	252799355	20260206	184942	전남87바4161	36.144376	128.298480	1	19.8	-19.8	0	NOUSE	\N	36.144376	128.29848	2026-02-06 09:51:32.529806+00	\N
440	\N	0013668	252227303	20260206	184722	전남87바4162	34.729060	126.596072	0	1.1	1.1	0	NOUSE	\N	34.72906	126.596072	2026-02-06 09:51:32.529806+00	\N
441	\N	0013668	251512429	20260206	185019	전남87바4165	37.246338	127.267346	1	23.1	-23.1	0	NOUSE	\N	37.246338	127.267346	2026-02-06 09:51:32.529806+00	\N
442	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 09:51:32.529806+00	\N
443	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 09:51:32.529806+00	\N
444	\N	0013668	251509223	20260206	184958	전남87바4173	36.684817	128.119248	1	23.1	-23.1	0	NOUSE	\N	36.684817	128.119248	2026-02-06 09:51:32.529806+00	\N
445	\N	0013668	252228112	20260206	185012	전남87바4174	35.258640	127.061000	1	22.3	-22.3	0	NOUSE	\N	35.25864	127.061	2026-02-06 09:51:32.529806+00	\N
446	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 09:51:32.529806+00	\N
447	\N	0013668	252214992	20260206	185012	전남87바4176	35.028824	127.868264	0	3.0	3	0	NOUSE	\N	35.028824	127.868264	2026-02-06 09:51:32.529806+00	\N
448	\N	0013668	239200586	20260206	184828	전남87바4177	36.094525	128.664688	0	5.7	5.7	0	NOUSE	\N	36.094525	128.664688	2026-02-06 09:51:32.529806+00	\N
449	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 09:51:32.529806+00	\N
450	\N	0013668	240074478	20260206	184605	전남87바4188	36.203784	127.266080	1	21.9	-21.9	0	NOUSE	\N	36.203784	127.26608	2026-02-06 09:51:32.529806+00	\N
451	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 09:51:32.529806+00	\N
452	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 09:56:32.569324+00	\N
453	\N	0013668	236275896	20260206	185326	전남87바1302	0.000000	0.000000	0	1.8	1.8	0	NOUSE	\N	0	0	2026-02-06 09:56:32.569324+00	\N
454	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 09:56:32.569324+00	\N
455	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 09:56:32.569324+00	\N
456	\N	0013668	252227307	20260206	185245	전남87바1305	35.287188	128.997944	0	4.1	4.1	0	NOUSE	\N	35.287188	128.997944	2026-02-06 09:56:32.569324+00	\N
457	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 09:56:32.569324+00	\N
458	\N	0013668	252713338	20260206	185427	전남87바1317	36.195784	127.261781	0	2.4	2.4	0	NOUSE	\N	36.195784	127.261781	2026-02-06 09:56:32.569324+00	\N
459	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 09:56:32.569324+00	\N
460	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 09:56:32.569324+00	\N
461	\N	0013668	249253808	20260206	185242	전남87바1325	36.403292	127.363184	1	21.7	-21.7	0	NOUSE	\N	36.403292	127.363184	2026-02-06 09:56:32.569324+00	\N
462	\N	0013668	252214998	20260206	180537	전남87바1326	35.290656	129.009640	1	22.3	-22.3	0	NOUSE	\N	35.290656	129.00964	2026-02-06 09:56:32.569324+00	\N
463	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 09:56:32.569324+00	\N
464	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 09:56:32.569324+00	\N
465	\N	0013668	251512431	20260206	185404	전남87바1351	37.248779	127.423626	1	22.1	-22.1	0	NOUSE	\N	37.248779	127.423626	2026-02-06 09:56:32.569324+00	\N
466	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 09:56:32.569324+00	\N
467	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 09:56:32.569324+00	\N
468	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 09:56:32.569324+00	\N
469	\N	0013668	236994200	20260206	185453	전남87바1362	36.565878	127.430099	0	1.5	1.5	0	2.8	2.8	36.565878	127.430099	2026-02-06 09:56:32.569324+00	\N
470	\N	0013668	252215001	20260206	185540	전남87바1364	37.018224	127.143816	0	3.5	3.5	0	NOUSE	\N	37.018224	127.143816	2026-02-06 09:56:32.569324+00	\N
471	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 09:56:32.569324+00	\N
472	\N	0013668	251512435	20260206	185142	전남87바1368	35.396437	128.832186	1	20.2	-20.2	0	0.7	0.7	35.396437	128.832186	2026-02-06 09:56:32.569324+00	\N
473	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 09:56:32.569324+00	\N
474	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 09:56:32.569324+00	\N
475	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 09:56:32.569324+00	\N
476	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 09:56:32.569324+00	\N
477	\N	0013668	235994979	20260206	185404	전남87바4157	35.239688	126.507768	0	5.4	5.4	0	NOUSE	\N	35.239688	126.507768	2026-02-06 09:56:32.569324+00	\N
478	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 09:56:32.569324+00	\N
479	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 09:56:32.569324+00	\N
480	\N	0013668	252799355	20260206	185442	전남87바4161	36.108672	128.360752	1	21.5	-21.5	0	NOUSE	\N	36.108672	128.360752	2026-02-06 09:56:32.569324+00	\N
481	\N	0013668	252227303	20260206	185222	전남87바4162	34.744936	126.538664	0	1.2	1.2	0	NOUSE	\N	34.744936	126.538664	2026-02-06 09:56:32.569324+00	\N
482	\N	0013668	251512429	20260206	185520	전남87바4165	37.235082	127.296947	1	21.5	-21.5	0	NOUSE	\N	37.235082	127.296947	2026-02-06 09:56:32.569324+00	\N
483	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 09:56:32.569324+00	\N
484	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 09:56:32.569324+00	\N
485	\N	0013668	251509223	20260206	185500	전남87바4173	36.634592	128.146643	1	21.8	-21.8	0	NOUSE	\N	36.634592	128.146643	2026-02-06 09:56:32.569324+00	\N
486	\N	0013668	252228112	20260206	185512	전남87바4174	35.251340	126.989376	1	23.2	-23.2	0	NOUSE	\N	35.25134	126.989376	2026-02-06 09:56:32.569324+00	\N
487	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 09:56:32.569324+00	\N
488	\N	0013668	252214992	20260206	185512	전남87바4176	34.997284	127.806920	0	2.9	2.9	0	NOUSE	\N	34.997284	127.80692	2026-02-06 09:56:32.569324+00	\N
489	\N	0013668	239200586	20260206	185329	전남87바4177	36.136390	128.602606	0	6.1	6.1	0	NOUSE	\N	36.13639	128.602606	2026-02-06 09:56:32.569324+00	\N
490	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 09:56:32.569324+00	\N
491	\N	0013668	240074478	20260206	185105	전남87바4188	36.158872	127.212144	1	21.5	-21.5	0	NOUSE	\N	36.158872	127.212144	2026-02-06 09:56:32.569324+00	\N
492	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 09:56:32.569324+00	\N
493	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 09:56:32.577159+00	\N
494	\N	0013668	236275896	20260206	185326	전남87바1302	0.000000	0.000000	0	1.8	1.8	0	NOUSE	\N	0	0	2026-02-06 09:56:32.577159+00	\N
495	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 09:56:32.577159+00	\N
496	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 09:56:32.577159+00	\N
497	\N	0013668	252227307	20260206	185245	전남87바1305	35.287188	128.997944	0	4.1	4.1	0	NOUSE	\N	35.287188	128.997944	2026-02-06 09:56:32.577159+00	\N
498	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 09:56:32.577159+00	\N
499	\N	0013668	252713338	20260206	185427	전남87바1317	36.195784	127.261781	0	2.4	2.4	0	NOUSE	\N	36.195784	127.261781	2026-02-06 09:56:32.577159+00	\N
500	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 09:56:32.577159+00	\N
501	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 09:56:32.577159+00	\N
502	\N	0013668	249253808	20260206	185242	전남87바1325	36.403292	127.363184	1	21.7	-21.7	0	NOUSE	\N	36.403292	127.363184	2026-02-06 09:56:32.577159+00	\N
503	\N	0013668	252214998	20260206	180537	전남87바1326	35.290656	129.009640	1	22.3	-22.3	0	NOUSE	\N	35.290656	129.00964	2026-02-06 09:56:32.577159+00	\N
504	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 09:56:32.577159+00	\N
505	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 09:56:32.577159+00	\N
506	\N	0013668	251512431	20260206	185404	전남87바1351	37.248779	127.423626	1	22.1	-22.1	0	NOUSE	\N	37.248779	127.423626	2026-02-06 09:56:32.577159+00	\N
507	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 09:56:32.577159+00	\N
508	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 09:56:32.577159+00	\N
509	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 09:56:32.577159+00	\N
510	\N	0013668	236994200	20260206	185453	전남87바1362	36.565878	127.430099	0	1.5	1.5	0	2.8	2.8	36.565878	127.430099	2026-02-06 09:56:32.577159+00	\N
511	\N	0013668	252215001	20260206	185540	전남87바1364	37.018224	127.143816	0	3.5	3.5	0	NOUSE	\N	37.018224	127.143816	2026-02-06 09:56:32.577159+00	\N
512	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 09:56:32.577159+00	\N
513	\N	0013668	251512435	20260206	185142	전남87바1368	35.396437	128.832186	1	20.2	-20.2	0	0.7	0.7	35.396437	128.832186	2026-02-06 09:56:32.577159+00	\N
514	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 09:56:32.577159+00	\N
515	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 09:56:32.577159+00	\N
516	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 09:56:32.577159+00	\N
517	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 09:56:32.577159+00	\N
518	\N	0013668	235994979	20260206	185404	전남87바4157	35.239688	126.507768	0	5.4	5.4	0	NOUSE	\N	35.239688	126.507768	2026-02-06 09:56:32.577159+00	\N
519	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 09:56:32.577159+00	\N
520	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 09:56:32.577159+00	\N
521	\N	0013668	252799355	20260206	185442	전남87바4161	36.108672	128.360752	1	21.5	-21.5	0	NOUSE	\N	36.108672	128.360752	2026-02-06 09:56:32.577159+00	\N
522	\N	0013668	252227303	20260206	185222	전남87바4162	34.744936	126.538664	0	1.2	1.2	0	NOUSE	\N	34.744936	126.538664	2026-02-06 09:56:32.577159+00	\N
523	\N	0013668	251512429	20260206	185520	전남87바4165	37.235082	127.296947	1	21.5	-21.5	0	NOUSE	\N	37.235082	127.296947	2026-02-06 09:56:32.577159+00	\N
524	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 09:56:32.577159+00	\N
525	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 09:56:32.577159+00	\N
526	\N	0013668	251509223	20260206	185500	전남87바4173	36.634592	128.146643	1	21.8	-21.8	0	NOUSE	\N	36.634592	128.146643	2026-02-06 09:56:32.577159+00	\N
527	\N	0013668	252228112	20260206	185512	전남87바4174	35.251340	126.989376	1	23.2	-23.2	0	NOUSE	\N	35.25134	126.989376	2026-02-06 09:56:32.577159+00	\N
528	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 09:56:32.577159+00	\N
529	\N	0013668	252214992	20260206	185512	전남87바4176	34.997284	127.806920	0	2.9	2.9	0	NOUSE	\N	34.997284	127.80692	2026-02-06 09:56:32.577159+00	\N
530	\N	0013668	239200586	20260206	185329	전남87바4177	36.136390	128.602606	0	6.1	6.1	0	NOUSE	\N	36.13639	128.602606	2026-02-06 09:56:32.577159+00	\N
531	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 09:56:32.577159+00	\N
532	\N	0013668	240074478	20260206	185105	전남87바4188	36.158872	127.212144	1	21.5	-21.5	0	NOUSE	\N	36.158872	127.212144	2026-02-06 09:56:32.577159+00	\N
533	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 09:56:32.577159+00	\N
534	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 09:56:32.632566+00	\N
535	\N	0013668	236275896	20260206	185326	전남87바1302	0.000000	0.000000	0	1.8	1.8	0	NOUSE	\N	0	0	2026-02-06 09:56:32.632566+00	\N
536	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 09:56:32.632566+00	\N
537	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 09:56:32.632566+00	\N
538	\N	0013668	252227307	20260206	185245	전남87바1305	35.287188	128.997944	0	4.1	4.1	0	NOUSE	\N	35.287188	128.997944	2026-02-06 09:56:32.632566+00	\N
539	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 09:56:32.632566+00	\N
540	\N	0013668	252713338	20260206	185427	전남87바1317	36.195784	127.261781	0	2.4	2.4	0	NOUSE	\N	36.195784	127.261781	2026-02-06 09:56:32.632566+00	\N
541	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 09:56:32.632566+00	\N
542	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 09:56:32.632566+00	\N
543	\N	0013668	249253808	20260206	185242	전남87바1325	36.403292	127.363184	1	21.7	-21.7	0	NOUSE	\N	36.403292	127.363184	2026-02-06 09:56:32.632566+00	\N
544	\N	0013668	252214998	20260206	180537	전남87바1326	35.290656	129.009640	1	22.3	-22.3	0	NOUSE	\N	35.290656	129.00964	2026-02-06 09:56:32.632566+00	\N
545	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 09:56:32.632566+00	\N
546	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 09:56:32.632566+00	\N
547	\N	0013668	251512431	20260206	185404	전남87바1351	37.248779	127.423626	1	22.1	-22.1	0	NOUSE	\N	37.248779	127.423626	2026-02-06 09:56:32.632566+00	\N
548	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 09:56:32.632566+00	\N
549	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 09:56:32.632566+00	\N
550	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 09:56:32.632566+00	\N
551	\N	0013668	236994200	20260206	185453	전남87바1362	36.565878	127.430099	0	1.5	1.5	0	2.8	2.8	36.565878	127.430099	2026-02-06 09:56:32.632566+00	\N
552	\N	0013668	252215001	20260206	185540	전남87바1364	37.018224	127.143816	0	3.5	3.5	0	NOUSE	\N	37.018224	127.143816	2026-02-06 09:56:32.632566+00	\N
553	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 09:56:32.632566+00	\N
554	\N	0013668	251512435	20260206	185142	전남87바1368	35.396437	128.832186	1	20.2	-20.2	0	0.7	0.7	35.396437	128.832186	2026-02-06 09:56:32.632566+00	\N
555	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 09:56:32.632566+00	\N
556	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 09:56:32.632566+00	\N
557	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 09:56:32.632566+00	\N
558	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 09:56:32.632566+00	\N
559	\N	0013668	235994979	20260206	185404	전남87바4157	35.239688	126.507768	0	5.4	5.4	0	NOUSE	\N	35.239688	126.507768	2026-02-06 09:56:32.632566+00	\N
560	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 09:56:32.632566+00	\N
561	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 09:56:32.632566+00	\N
562	\N	0013668	252799355	20260206	185442	전남87바4161	36.108672	128.360752	1	21.5	-21.5	0	NOUSE	\N	36.108672	128.360752	2026-02-06 09:56:32.632566+00	\N
563	\N	0013668	252227303	20260206	185222	전남87바4162	34.744936	126.538664	0	1.2	1.2	0	NOUSE	\N	34.744936	126.538664	2026-02-06 09:56:32.632566+00	\N
564	\N	0013668	251512429	20260206	185520	전남87바4165	37.235082	127.296947	1	21.5	-21.5	0	NOUSE	\N	37.235082	127.296947	2026-02-06 09:56:32.632566+00	\N
565	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 09:56:32.632566+00	\N
566	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 09:56:32.632566+00	\N
567	\N	0013668	251509223	20260206	185500	전남87바4173	36.634592	128.146643	1	21.8	-21.8	0	NOUSE	\N	36.634592	128.146643	2026-02-06 09:56:32.632566+00	\N
568	\N	0013668	252228112	20260206	185512	전남87바4174	35.251340	126.989376	1	23.2	-23.2	0	NOUSE	\N	35.25134	126.989376	2026-02-06 09:56:32.632566+00	\N
569	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 09:56:32.632566+00	\N
570	\N	0013668	252214992	20260206	185512	전남87바4176	34.997284	127.806920	0	2.9	2.9	0	NOUSE	\N	34.997284	127.80692	2026-02-06 09:56:32.632566+00	\N
571	\N	0013668	239200586	20260206	185329	전남87바4177	36.136390	128.602606	0	6.1	6.1	0	NOUSE	\N	36.13639	128.602606	2026-02-06 09:56:32.632566+00	\N
572	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 09:56:32.632566+00	\N
573	\N	0013668	240074478	20260206	185105	전남87바4188	36.158872	127.212144	1	21.5	-21.5	0	NOUSE	\N	36.158872	127.212144	2026-02-06 09:56:32.632566+00	\N
574	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 09:56:32.632566+00	\N
575	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 09:56:32.66955+00	\N
576	\N	0013668	236275896	20260206	185326	전남87바1302	0.000000	0.000000	0	1.8	1.8	0	NOUSE	\N	0	0	2026-02-06 09:56:32.66955+00	\N
577	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 09:56:32.66955+00	\N
578	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 09:56:32.66955+00	\N
579	\N	0013668	252227307	20260206	185245	전남87바1305	35.287188	128.997944	0	4.1	4.1	0	NOUSE	\N	35.287188	128.997944	2026-02-06 09:56:32.66955+00	\N
580	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 09:56:32.66955+00	\N
581	\N	0013668	252713338	20260206	185427	전남87바1317	36.195784	127.261781	0	2.4	2.4	0	NOUSE	\N	36.195784	127.261781	2026-02-06 09:56:32.66955+00	\N
582	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 09:56:32.66955+00	\N
583	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 09:56:32.66955+00	\N
584	\N	0013668	249253808	20260206	185242	전남87바1325	36.403292	127.363184	1	21.7	-21.7	0	NOUSE	\N	36.403292	127.363184	2026-02-06 09:56:32.66955+00	\N
585	\N	0013668	252214998	20260206	180537	전남87바1326	35.290656	129.009640	1	22.3	-22.3	0	NOUSE	\N	35.290656	129.00964	2026-02-06 09:56:32.66955+00	\N
586	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 09:56:32.66955+00	\N
587	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 09:56:32.66955+00	\N
588	\N	0013668	251512431	20260206	185404	전남87바1351	37.248779	127.423626	1	22.1	-22.1	0	NOUSE	\N	37.248779	127.423626	2026-02-06 09:56:32.66955+00	\N
589	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 09:56:32.66955+00	\N
590	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 09:56:32.66955+00	\N
591	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 09:56:32.66955+00	\N
592	\N	0013668	236994200	20260206	185453	전남87바1362	36.565878	127.430099	0	1.5	1.5	0	2.8	2.8	36.565878	127.430099	2026-02-06 09:56:32.66955+00	\N
593	\N	0013668	252215001	20260206	185540	전남87바1364	37.018224	127.143816	0	3.5	3.5	0	NOUSE	\N	37.018224	127.143816	2026-02-06 09:56:32.66955+00	\N
594	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 09:56:32.66955+00	\N
595	\N	0013668	251512435	20260206	185142	전남87바1368	35.396437	128.832186	1	20.2	-20.2	0	0.7	0.7	35.396437	128.832186	2026-02-06 09:56:32.66955+00	\N
596	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 09:56:32.66955+00	\N
597	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 09:56:32.66955+00	\N
598	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 09:56:32.66955+00	\N
599	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 09:56:32.66955+00	\N
600	\N	0013668	235994979	20260206	185404	전남87바4157	35.239688	126.507768	0	5.4	5.4	0	NOUSE	\N	35.239688	126.507768	2026-02-06 09:56:32.66955+00	\N
601	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 09:56:32.66955+00	\N
602	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 09:56:32.66955+00	\N
603	\N	0013668	252799355	20260206	185442	전남87바4161	36.108672	128.360752	1	21.5	-21.5	0	NOUSE	\N	36.108672	128.360752	2026-02-06 09:56:32.66955+00	\N
604	\N	0013668	252227303	20260206	185222	전남87바4162	34.744936	126.538664	0	1.2	1.2	0	NOUSE	\N	34.744936	126.538664	2026-02-06 09:56:32.66955+00	\N
605	\N	0013668	251512429	20260206	185520	전남87바4165	37.235082	127.296947	1	21.5	-21.5	0	NOUSE	\N	37.235082	127.296947	2026-02-06 09:56:32.66955+00	\N
606	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 09:56:32.66955+00	\N
607	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 09:56:32.66955+00	\N
608	\N	0013668	251509223	20260206	185500	전남87바4173	36.634592	128.146643	1	21.8	-21.8	0	NOUSE	\N	36.634592	128.146643	2026-02-06 09:56:32.66955+00	\N
609	\N	0013668	252228112	20260206	185512	전남87바4174	35.251340	126.989376	1	23.2	-23.2	0	NOUSE	\N	35.25134	126.989376	2026-02-06 09:56:32.66955+00	\N
610	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 09:56:32.66955+00	\N
611	\N	0013668	252214992	20260206	185512	전남87바4176	34.997284	127.806920	0	2.9	2.9	0	NOUSE	\N	34.997284	127.80692	2026-02-06 09:56:32.66955+00	\N
612	\N	0013668	239200586	20260206	185329	전남87바4177	36.136390	128.602606	0	6.1	6.1	0	NOUSE	\N	36.13639	128.602606	2026-02-06 09:56:32.66955+00	\N
613	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 09:56:32.66955+00	\N
614	\N	0013668	240074478	20260206	185105	전남87바4188	36.158872	127.212144	1	21.5	-21.5	0	NOUSE	\N	36.158872	127.212144	2026-02-06 09:56:32.66955+00	\N
615	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 09:56:32.66955+00	\N
616	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:05:14.367402+00	\N
617	\N	0013668	236275896	20260206	190326	전남87바1302	0.000000	0.000000	0	1.8	1.8	0	NOUSE	\N	0	0	2026-02-06 10:05:14.367402+00	\N
618	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:05:14.367402+00	\N
619	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:05:14.367402+00	\N
620	\N	0013668	252227307	20260206	190245	전남87바1305	35.374392	129.050616	0	4.2	4.2	0	NOUSE	\N	35.374392	129.050616	2026-02-06 10:05:14.367402+00	\N
621	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 10:05:14.367402+00	\N
622	\N	0013668	252713338	20260206	190431	전남87바1317	36.292539	127.316835	0	2.6	2.6	0	NOUSE	\N	36.292539	127.316835	2026-02-06 10:05:14.367402+00	\N
623	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:05:14.367402+00	\N
624	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:05:14.367402+00	\N
625	\N	0013668	249253808	20260206	190242	전남87바1325	36.468116	127.422336	1	18.9	-18.9	0	NOUSE	\N	36.468116	127.422336	2026-02-06 10:05:14.367402+00	\N
626	\N	0013668	252214998	20260206	180537	전남87바1326	35.290656	129.009640	1	22.3	-22.3	0	NOUSE	\N	35.290656	129.00964	2026-02-06 10:05:14.367402+00	\N
627	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:05:14.367402+00	\N
628	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:05:14.367402+00	\N
629	\N	0013668	251512431	20260206	190409	전남87바1351	37.248751	127.423680	1	24.0	-24	0	NOUSE	\N	37.248751	127.42368	2026-02-06 10:05:14.367402+00	\N
630	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:05:14.367402+00	\N
631	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:05:14.367402+00	\N
632	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:05:14.367402+00	\N
633	\N	0013668	236994200	20260206	190457	전남87바1362	36.445771	127.419024	0	1.6	1.6	0	2.9	2.9	36.445771	127.419024	2026-02-06 10:05:14.367402+00	\N
634	\N	0013668	252215001	20260206	190040	전남87바1364	37.032192	127.160208	0	3.6	3.6	0	NOUSE	\N	37.032192	127.160208	2026-02-06 10:05:14.367402+00	\N
635	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:05:14.367402+00	\N
636	\N	0013668	251512435	20260206	185643	전남87바1368	35.374363	128.831363	1	19.7	-19.7	0	0.2	0.2	35.374363	128.831363	2026-02-06 10:05:14.367402+00	\N
637	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:05:14.367402+00	\N
638	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:05:14.367402+00	\N
639	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:05:14.367402+00	\N
640	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:05:14.367402+00	\N
641	\N	0013668	235994979	20260206	190404	전남87바4157	35.354028	126.582192	0	5.4	5.4	0	NOUSE	\N	35.354028	126.582192	2026-02-06 10:05:14.367402+00	\N
642	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:05:14.367402+00	\N
643	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:05:14.367402+00	\N
644	\N	0013668	252799355	20260206	190442	전남87바4161	36.016840	128.430312	1	20.6	-20.6	0	NOUSE	\N	36.01684	128.430312	2026-02-06 10:05:14.367402+00	\N
645	\N	0013668	252227303	20260206	190222	전남87바4162	34.848132	126.470352	0	1.7	1.7	0	NOUSE	\N	34.848132	126.470352	2026-02-06 10:05:14.367402+00	\N
646	\N	0013668	251512429	20260206	190022	전남87바4165	37.206957	127.322990	1	23.0	-23	0	NOUSE	\N	37.206957	127.32299	2026-02-06 10:05:14.367402+00	\N
647	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:05:14.367402+00	\N
648	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:05:14.367402+00	\N
649	\N	0013668	251509223	20260206	190504	전남87바4173	36.538714	128.152804	1	21.3	-21.3	0	NOUSE	\N	36.538714	128.152804	2026-02-06 10:05:14.367402+00	\N
650	\N	0013668	252228112	20260206	190012	전남87바4174	35.253916	126.910416	1	25.5	-25.5	0	NOUSE	\N	35.253916	126.910416	2026-02-06 10:05:14.367402+00	\N
651	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:05:14.367402+00	\N
652	\N	0013668	252214992	20260206	190012	전남87바4176	34.980608	127.737080	0	2.6	2.6	0	NOUSE	\N	34.980608	127.73708	2026-02-06 10:05:14.367402+00	\N
653	\N	0013668	239200586	20260206	190333	전남87바4177	36.229127	128.506895	0	6.4	6.4	0	NOUSE	\N	36.229127	128.506895	2026-02-06 10:05:14.367402+00	\N
654	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:05:14.367402+00	\N
655	\N	0013668	240074478	20260206	190105	전남87바4188	36.087396	127.105520	1	20.9	-20.9	0	NOUSE	\N	36.087396	127.10552	2026-02-06 10:05:14.367402+00	\N
656	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:05:14.367402+00	\N
657	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:05:14.372386+00	\N
659	\N	0013668	236275896	20260206	190326	전남87바1302	0.000000	0.000000	0	1.8	1.8	0	NOUSE	\N	0	0	2026-02-06 10:05:14.372386+00	\N
660	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:05:14.372386+00	\N
661	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:05:14.372386+00	\N
662	\N	0013668	252227307	20260206	190245	전남87바1305	35.374392	129.050616	0	4.2	4.2	0	NOUSE	\N	35.374392	129.050616	2026-02-06 10:05:14.372386+00	\N
663	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 10:05:14.372386+00	\N
664	\N	0013668	252713338	20260206	190431	전남87바1317	36.292539	127.316835	0	2.6	2.6	0	NOUSE	\N	36.292539	127.316835	2026-02-06 10:05:14.372386+00	\N
665	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:05:14.372386+00	\N
666	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:05:14.372386+00	\N
667	\N	0013668	249253808	20260206	190242	전남87바1325	36.468116	127.422336	1	18.9	-18.9	0	NOUSE	\N	36.468116	127.422336	2026-02-06 10:05:14.372386+00	\N
668	\N	0013668	252214998	20260206	180537	전남87바1326	35.290656	129.009640	1	22.3	-22.3	0	NOUSE	\N	35.290656	129.00964	2026-02-06 10:05:14.372386+00	\N
669	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:05:14.372386+00	\N
670	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:05:14.372386+00	\N
658	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:05:14.375624+00	\N
671	\N	0013668	251512431	20260206	190409	전남87바1351	37.248751	127.423680	1	24.0	-24	0	NOUSE	\N	37.248751	127.42368	2026-02-06 10:05:14.372386+00	\N
672	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:05:14.372386+00	\N
673	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:05:14.372386+00	\N
674	\N	0013668	236275896	20260206	190326	전남87바1302	0.000000	0.000000	0	1.8	1.8	0	NOUSE	\N	0	0	2026-02-06 10:05:14.375624+00	\N
675	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:05:14.375624+00	\N
676	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:05:14.375624+00	\N
677	\N	0013668	252227307	20260206	190245	전남87바1305	35.374392	129.050616	0	4.2	4.2	0	NOUSE	\N	35.374392	129.050616	2026-02-06 10:05:14.375624+00	\N
678	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 10:05:14.375624+00	\N
679	\N	0013668	252713338	20260206	190431	전남87바1317	36.292539	127.316835	0	2.6	2.6	0	NOUSE	\N	36.292539	127.316835	2026-02-06 10:05:14.375624+00	\N
680	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:05:14.375624+00	\N
681	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:05:14.375624+00	\N
682	\N	0013668	249253808	20260206	190242	전남87바1325	36.468116	127.422336	1	18.9	-18.9	0	NOUSE	\N	36.468116	127.422336	2026-02-06 10:05:14.375624+00	\N
683	\N	0013668	252214998	20260206	180537	전남87바1326	35.290656	129.009640	1	22.3	-22.3	0	NOUSE	\N	35.290656	129.00964	2026-02-06 10:05:14.375624+00	\N
684	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:05:14.375624+00	\N
685	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:05:14.375624+00	\N
686	\N	0013668	251512431	20260206	190409	전남87바1351	37.248751	127.423680	1	24.0	-24	0	NOUSE	\N	37.248751	127.42368	2026-02-06 10:05:14.375624+00	\N
687	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:05:14.375624+00	\N
688	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:05:14.375624+00	\N
689	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:05:14.375624+00	\N
690	\N	0013668	236994200	20260206	190457	전남87바1362	36.445771	127.419024	0	1.6	1.6	0	2.9	2.9	36.445771	127.419024	2026-02-06 10:05:14.375624+00	\N
691	\N	0013668	252215001	20260206	190040	전남87바1364	37.032192	127.160208	0	3.6	3.6	0	NOUSE	\N	37.032192	127.160208	2026-02-06 10:05:14.375624+00	\N
692	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:05:14.375624+00	\N
693	\N	0013668	251512435	20260206	185643	전남87바1368	35.374363	128.831363	1	19.7	-19.7	0	0.2	0.2	35.374363	128.831363	2026-02-06 10:05:14.375624+00	\N
694	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:05:14.375624+00	\N
695	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:05:14.375624+00	\N
696	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:05:14.375624+00	\N
697	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:05:14.375624+00	\N
698	\N	0013668	235994979	20260206	190404	전남87바4157	35.354028	126.582192	0	5.4	5.4	0	NOUSE	\N	35.354028	126.582192	2026-02-06 10:05:14.375624+00	\N
699	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:05:14.375624+00	\N
700	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:05:14.375624+00	\N
701	\N	0013668	252799355	20260206	190442	전남87바4161	36.016840	128.430312	1	20.6	-20.6	0	NOUSE	\N	36.01684	128.430312	2026-02-06 10:05:14.375624+00	\N
702	\N	0013668	252227303	20260206	190222	전남87바4162	34.848132	126.470352	0	1.7	1.7	0	NOUSE	\N	34.848132	126.470352	2026-02-06 10:05:14.375624+00	\N
703	\N	0013668	251512429	20260206	190022	전남87바4165	37.206957	127.322990	1	23.0	-23	0	NOUSE	\N	37.206957	127.32299	2026-02-06 10:05:14.375624+00	\N
704	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:05:14.375624+00	\N
705	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:05:14.375624+00	\N
706	\N	0013668	251509223	20260206	190504	전남87바4173	36.538714	128.152804	1	21.3	-21.3	0	NOUSE	\N	36.538714	128.152804	2026-02-06 10:05:14.375624+00	\N
707	\N	0013668	252228112	20260206	190012	전남87바4174	35.253916	126.910416	1	25.5	-25.5	0	NOUSE	\N	35.253916	126.910416	2026-02-06 10:05:14.375624+00	\N
708	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:05:14.375624+00	\N
709	\N	0013668	252214992	20260206	190012	전남87바4176	34.980608	127.737080	0	2.6	2.6	0	NOUSE	\N	34.980608	127.73708	2026-02-06 10:05:14.375624+00	\N
710	\N	0013668	239200586	20260206	190333	전남87바4177	36.229127	128.506895	0	6.4	6.4	0	NOUSE	\N	36.229127	128.506895	2026-02-06 10:05:14.375624+00	\N
711	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:05:14.375624+00	\N
712	\N	0013668	240074478	20260206	190105	전남87바4188	36.087396	127.105520	1	20.9	-20.9	0	NOUSE	\N	36.087396	127.10552	2026-02-06 10:05:14.375624+00	\N
713	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:05:14.375624+00	\N
1336	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:52:02.909905+00	\N
1337	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:52:02.909905+00	\N
1338	\N	0013668	235994979	20260206	194904	전남87바4157	35.671572	126.733704	0	5.2	5.2	0	NOUSE	\N	35.671572	126.733704	2026-02-06 10:52:02.909905+00	\N
1339	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:52:02.909905+00	\N
1340	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:52:02.909905+00	\N
1341	\N	0013668	252799355	20260206	194942	전남87바4161	35.656756	128.745792	1	19.6	-19.6	0	NOUSE	\N	35.656756	128.745792	2026-02-06 10:52:02.909905+00	\N
1342	\N	0013668	252227303	20260206	194722	전남87바4162	35.384144	126.612832	0	2.7	2.7	0	NOUSE	\N	35.384144	126.612832	2026-02-06 10:52:02.909905+00	\N
1343	\N	0013668	251512429	20260206	191528	전남87바4165	37.147991	127.384745	1	21.8	-21.8	0	NOUSE	\N	37.147991	127.384745	2026-02-06 10:52:02.909905+00	\N
1344	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:52:02.909905+00	\N
1345	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:52:02.909905+00	\N
1346	\N	0013668	251509223	20260206	195021	전남87바4173	36.107702	128.361054	1	19.7	-19.7	0	NOUSE	\N	36.107702	128.361054	2026-02-06 10:52:02.909905+00	\N
1347	\N	0013668	252228112	20260206	192012	전남87바4174	35.320380	126.754328	1	21.1	-21.1	0	NOUSE	\N	35.32038	126.754328	2026-02-06 10:52:02.909905+00	\N
1348	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:52:02.909905+00	\N
1349	\N	0013668	252214992	20260206	195012	전남87바4176	35.210612	127.235072	0	2.6	2.6	0	NOUSE	\N	35.210612	127.235072	2026-02-06 10:52:02.909905+00	\N
1350	\N	0013668	239200586	20260206	194850	전남87바4177	36.619811	128.152410	0	5.8	5.8	0	NOUSE	\N	36.619811	128.15241	2026-02-06 10:52:02.909905+00	\N
1351	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:52:02.909905+00	\N
714	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:05:14.372386+00	\N
715	\N	0013668	236994200	20260206	190457	전남87바1362	36.445771	127.419024	0	1.6	1.6	0	2.9	2.9	36.445771	127.419024	2026-02-06 10:05:14.372386+00	\N
716	\N	0013668	252215001	20260206	190040	전남87바1364	37.032192	127.160208	0	3.6	3.6	0	NOUSE	\N	37.032192	127.160208	2026-02-06 10:05:14.372386+00	\N
717	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:05:14.372386+00	\N
718	\N	0013668	251512435	20260206	185643	전남87바1368	35.374363	128.831363	1	19.7	-19.7	0	0.2	0.2	35.374363	128.831363	2026-02-06 10:05:14.372386+00	\N
719	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:05:14.372386+00	\N
720	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:05:14.372386+00	\N
721	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:05:14.372386+00	\N
722	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:05:14.372386+00	\N
723	\N	0013668	235994979	20260206	190404	전남87바4157	35.354028	126.582192	0	5.4	5.4	0	NOUSE	\N	35.354028	126.582192	2026-02-06 10:05:14.372386+00	\N
724	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:05:14.372386+00	\N
725	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:05:14.372386+00	\N
726	\N	0013668	252799355	20260206	190442	전남87바4161	36.016840	128.430312	1	20.6	-20.6	0	NOUSE	\N	36.01684	128.430312	2026-02-06 10:05:14.372386+00	\N
727	\N	0013668	252227303	20260206	190222	전남87바4162	34.848132	126.470352	0	1.7	1.7	0	NOUSE	\N	34.848132	126.470352	2026-02-06 10:05:14.372386+00	\N
728	\N	0013668	251512429	20260206	190022	전남87바4165	37.206957	127.322990	1	23.0	-23	0	NOUSE	\N	37.206957	127.32299	2026-02-06 10:05:14.372386+00	\N
729	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:05:14.372386+00	\N
730	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:05:14.372386+00	\N
731	\N	0013668	251509223	20260206	190504	전남87바4173	36.538714	128.152804	1	21.3	-21.3	0	NOUSE	\N	36.538714	128.152804	2026-02-06 10:05:14.372386+00	\N
732	\N	0013668	252228112	20260206	190012	전남87바4174	35.253916	126.910416	1	25.5	-25.5	0	NOUSE	\N	35.253916	126.910416	2026-02-06 10:05:14.372386+00	\N
733	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:05:14.372386+00	\N
734	\N	0013668	252214992	20260206	190012	전남87바4176	34.980608	127.737080	0	2.6	2.6	0	NOUSE	\N	34.980608	127.73708	2026-02-06 10:05:14.372386+00	\N
735	\N	0013668	239200586	20260206	190333	전남87바4177	36.229127	128.506895	0	6.4	6.4	0	NOUSE	\N	36.229127	128.506895	2026-02-06 10:05:14.372386+00	\N
736	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:05:14.372386+00	\N
737	\N	0013668	240074478	20260206	190105	전남87바4188	36.087396	127.105520	1	20.9	-20.9	0	NOUSE	\N	36.087396	127.10552	2026-02-06 10:05:14.372386+00	\N
738	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:05:14.372386+00	\N
739	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:05:14.369228+00	\N
740	\N	0013668	236275896	20260206	190326	전남87바1302	0.000000	0.000000	0	1.8	1.8	0	NOUSE	\N	0	0	2026-02-06 10:05:14.369228+00	\N
741	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:05:14.369228+00	\N
742	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:05:14.369228+00	\N
743	\N	0013668	252227307	20260206	190245	전남87바1305	35.374392	129.050616	0	4.2	4.2	0	NOUSE	\N	35.374392	129.050616	2026-02-06 10:05:14.369228+00	\N
744	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 10:05:14.369228+00	\N
745	\N	0013668	252713338	20260206	190431	전남87바1317	36.292539	127.316835	0	2.6	2.6	0	NOUSE	\N	36.292539	127.316835	2026-02-06 10:05:14.369228+00	\N
746	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:05:14.369228+00	\N
747	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:05:14.369228+00	\N
748	\N	0013668	249253808	20260206	190242	전남87바1325	36.468116	127.422336	1	18.9	-18.9	0	NOUSE	\N	36.468116	127.422336	2026-02-06 10:05:14.369228+00	\N
749	\N	0013668	252214998	20260206	180537	전남87바1326	35.290656	129.009640	1	22.3	-22.3	0	NOUSE	\N	35.290656	129.00964	2026-02-06 10:05:14.369228+00	\N
750	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:05:14.369228+00	\N
751	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:05:14.369228+00	\N
752	\N	0013668	251512431	20260206	190409	전남87바1351	37.248751	127.423680	1	24.0	-24	0	NOUSE	\N	37.248751	127.42368	2026-02-06 10:05:14.369228+00	\N
753	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:05:14.369228+00	\N
754	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:05:14.369228+00	\N
755	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:05:14.369228+00	\N
756	\N	0013668	236994200	20260206	190457	전남87바1362	36.445771	127.419024	0	1.6	1.6	0	2.9	2.9	36.445771	127.419024	2026-02-06 10:05:14.369228+00	\N
757	\N	0013668	252215001	20260206	190040	전남87바1364	37.032192	127.160208	0	3.6	3.6	0	NOUSE	\N	37.032192	127.160208	2026-02-06 10:05:14.369228+00	\N
758	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:05:14.369228+00	\N
759	\N	0013668	251512435	20260206	185643	전남87바1368	35.374363	128.831363	1	19.7	-19.7	0	0.2	0.2	35.374363	128.831363	2026-02-06 10:05:14.369228+00	\N
760	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:05:14.369228+00	\N
761	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:05:14.369228+00	\N
762	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:05:14.369228+00	\N
763	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:05:14.369228+00	\N
764	\N	0013668	235994979	20260206	190404	전남87바4157	35.354028	126.582192	0	5.4	5.4	0	NOUSE	\N	35.354028	126.582192	2026-02-06 10:05:14.369228+00	\N
765	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:05:14.369228+00	\N
766	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:05:14.369228+00	\N
767	\N	0013668	252799355	20260206	190442	전남87바4161	36.016840	128.430312	1	20.6	-20.6	0	NOUSE	\N	36.01684	128.430312	2026-02-06 10:05:14.369228+00	\N
768	\N	0013668	252227303	20260206	190222	전남87바4162	34.848132	126.470352	0	1.7	1.7	0	NOUSE	\N	34.848132	126.470352	2026-02-06 10:05:14.369228+00	\N
769	\N	0013668	251512429	20260206	190022	전남87바4165	37.206957	127.322990	1	23.0	-23	0	NOUSE	\N	37.206957	127.32299	2026-02-06 10:05:14.369228+00	\N
770	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:05:14.369228+00	\N
771	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:05:14.369228+00	\N
772	\N	0013668	251509223	20260206	190504	전남87바4173	36.538714	128.152804	1	21.3	-21.3	0	NOUSE	\N	36.538714	128.152804	2026-02-06 10:05:14.369228+00	\N
773	\N	0013668	252228112	20260206	190012	전남87바4174	35.253916	126.910416	1	25.5	-25.5	0	NOUSE	\N	35.253916	126.910416	2026-02-06 10:05:14.369228+00	\N
774	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:05:14.369228+00	\N
775	\N	0013668	252214992	20260206	190012	전남87바4176	34.980608	127.737080	0	2.6	2.6	0	NOUSE	\N	34.980608	127.73708	2026-02-06 10:05:14.369228+00	\N
776	\N	0013668	239200586	20260206	190333	전남87바4177	36.229127	128.506895	0	6.4	6.4	0	NOUSE	\N	36.229127	128.506895	2026-02-06 10:05:14.369228+00	\N
777	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:05:14.369228+00	\N
778	\N	0013668	240074478	20260206	190105	전남87바4188	36.087396	127.105520	1	20.9	-20.9	0	NOUSE	\N	36.087396	127.10552	2026-02-06 10:05:14.369228+00	\N
779	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:05:14.369228+00	\N
780	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:10:14.039611+00	\N
781	\N	0013668	236275896	20260206	190826	전남87바1302	0.000000	0.000000	0	1.7	1.7	0	NOUSE	\N	0	0	2026-02-06 10:10:14.039611+00	\N
782	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:10:14.039611+00	\N
783	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:10:14.039611+00	\N
784	\N	0013668	252227307	20260206	190745	전남87바1305	35.380012	129.048664	0	4.2	4.2	0	NOUSE	\N	35.380012	129.048664	2026-02-06 10:10:14.039611+00	\N
785	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 10:10:14.039611+00	\N
786	\N	0013668	252713338	20260206	190933	전남87바1317	36.348280	127.323511	0	2.6	2.6	0	NOUSE	\N	36.34828	127.323511	2026-02-06 10:10:14.039611+00	\N
787	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:10:14.039611+00	\N
788	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:10:14.039611+00	\N
789	\N	0013668	249253808	20260206	190742	전남87바1325	36.528700	127.430976	1	22.1	-22.1	0	NOUSE	\N	36.5287	127.430976	2026-02-06 10:10:14.039611+00	\N
790	\N	0013668	252214998	20260206	180537	전남87바1326	35.290656	129.009640	1	22.3	-22.3	0	NOUSE	\N	35.290656	129.00964	2026-02-06 10:10:14.039611+00	\N
791	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:10:14.039611+00	\N
792	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:10:14.039611+00	\N
793	\N	0013668	251512431	20260206	190910	전남87바1351	37.248838	127.423753	1	25.1	-25.1	0	NOUSE	\N	37.248838	127.423753	2026-02-06 10:10:14.039611+00	\N
794	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:10:14.039611+00	\N
795	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:10:14.039611+00	\N
796	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:10:14.039611+00	\N
797	\N	0013668	236994200	20260206	190958	전남87바1362	36.408248	127.401085	0	1.6	1.6	0	2.9	2.9	36.408248	127.401085	2026-02-06 10:10:14.039611+00	\N
798	\N	0013668	252215001	20260206	190540	전남87바1364	0.000000	0.000000	0	3.6	3.6	0	NOUSE	\N	0	0	2026-02-06 10:10:14.039611+00	\N
799	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:10:14.039611+00	\N
800	\N	0013668	251512435	20260206	185643	전남87바1368	35.374363	128.831363	1	19.7	-19.7	0	0.2	0.2	35.374363	128.831363	2026-02-06 10:10:14.039611+00	\N
801	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:10:14.039611+00	\N
802	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:10:14.039611+00	\N
803	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:10:14.039611+00	\N
804	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:10:14.039611+00	\N
805	\N	0013668	235994979	20260206	190904	전남87바4157	35.402188	126.635928	0	5.4	5.4	0	NOUSE	\N	35.402188	126.635928	2026-02-06 10:10:14.039611+00	\N
806	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:10:14.039611+00	\N
807	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:10:14.039611+00	\N
808	\N	0013668	252799355	20260206	190942	전남87바4161	35.960216	128.454072	1	22.9	-22.9	0	NOUSE	\N	35.960216	128.454072	2026-02-06 10:10:14.039611+00	\N
809	\N	0013668	252227303	20260206	190722	전남87바4162	34.890664	126.498608	0	1.7	1.7	0	NOUSE	\N	34.890664	126.498608	2026-02-06 10:10:14.039611+00	\N
810	\N	0013668	251512429	20260206	190524	전남87바4165	37.173100	127.348651	1	21.6	-21.6	0	NOUSE	\N	37.1731	127.348651	2026-02-06 10:10:14.039611+00	\N
811	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:10:14.039611+00	\N
812	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:10:14.039611+00	\N
813	\N	0013668	251509223	20260206	191006	전남87바4173	36.494428	128.192665	1	22.5	-22.5	0	NOUSE	\N	36.494428	128.192665	2026-02-06 10:10:14.039611+00	\N
814	\N	0013668	252228112	20260206	190512	전남87바4174	0.000000	0.000000	1	20.6	-20.6	0	NOUSE	\N	0	0	2026-02-06 10:10:14.039611+00	\N
815	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:10:14.039611+00	\N
816	\N	0013668	252214992	20260206	190512	전남87바4176	34.981176	127.675280	0	2.0	2	0	NOUSE	\N	34.981176	127.67528	2026-02-06 10:10:14.039611+00	\N
817	\N	0013668	239200586	20260206	190836	전남87바4177	36.260180	128.438019	0	6.6	6.6	0	NOUSE	\N	36.26018	128.438019	2026-02-06 10:10:14.039611+00	\N
818	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:10:14.039611+00	\N
819	\N	0013668	240074478	20260206	190605	전남87바4188	36.025104	127.103168	1	22.2	-22.2	0	NOUSE	\N	36.025104	127.103168	2026-02-06 10:10:14.039611+00	\N
820	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:10:14.039611+00	\N
821	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:15:14.08301+00	\N
822	\N	0013668	236275896	20260206	191326	전남87바1302	0.000000	0.000000	0	1.7	1.7	0	NOUSE	\N	0	0	2026-02-06 10:15:14.08301+00	\N
823	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:15:14.08301+00	\N
824	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:15:14.08301+00	\N
825	\N	0013668	252227307	20260206	191245	전남87바1305	35.372084	129.021760	0	4.2	4.2	0	NOUSE	\N	35.372084	129.02176	2026-02-06 10:15:14.08301+00	\N
826	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 10:15:14.08301+00	\N
827	\N	0013668	252713338	20260206	191435	전남87바1317	36.398799	127.356617	0	2.6	2.6	0	NOUSE	\N	36.398799	127.356617	2026-02-06 10:15:14.08301+00	\N
828	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:15:14.08301+00	\N
829	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:15:14.08301+00	\N
830	\N	0013668	249253808	20260206	191242	전남87바1325	36.590060	127.426664	1	22.5	-22.5	0	NOUSE	\N	36.59006	127.426664	2026-02-06 10:15:14.08301+00	\N
831	\N	0013668	252214998	20260206	191037	전남87바1326	35.386044	129.015808	1	11.9	-11.9	0	NOUSE	\N	35.386044	129.015808	2026-02-06 10:15:14.08301+00	\N
832	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:15:14.08301+00	\N
833	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:15:14.08301+00	\N
834	\N	0013668	251512431	20260206	190910	전남87바1351	37.248838	127.423753	1	25.1	-25.1	0	NOUSE	\N	37.248838	127.423753	2026-02-06 10:15:14.08301+00	\N
835	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:15:14.08301+00	\N
836	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:15:14.08301+00	\N
837	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:15:14.08301+00	\N
838	\N	0013668	236994200	20260206	191501	전남87바1362	36.388446	127.339464	0	1.7	1.7	0	2.8	2.8	36.388446	127.339464	2026-02-06 10:15:14.08301+00	\N
839	\N	0013668	252215001	20260206	191040	전남87바1364	37.086812	127.207872	0	3.5	3.5	0	NOUSE	\N	37.086812	127.207872	2026-02-06 10:15:14.08301+00	\N
840	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:15:14.08301+00	\N
841	\N	0013668	251512435	20260206	185643	전남87바1368	35.374363	128.831363	1	19.7	-19.7	0	0.2	0.2	35.374363	128.831363	2026-02-06 10:15:14.08301+00	\N
842	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:15:14.08301+00	\N
843	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:15:14.08301+00	\N
844	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:15:14.08301+00	\N
845	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:15:14.08301+00	\N
846	\N	0013668	235994979	20260206	191404	전남87바4157	35.460108	126.670968	0	5.4	5.4	0	NOUSE	\N	35.460108	126.670968	2026-02-06 10:15:14.08301+00	\N
847	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:15:14.08301+00	\N
848	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:15:14.08301+00	\N
849	\N	0013668	252799355	20260206	191442	전남87바4161	35.904960	128.492520	1	19.4	-19.4	0	NOUSE	\N	35.90496	128.49252	2026-02-06 10:15:14.08301+00	\N
850	\N	0013668	252227303	20260206	191222	전남87바4162	34.955180	126.502696	0	1.8	1.8	0	NOUSE	\N	34.95518	126.502696	2026-02-06 10:15:14.08301+00	\N
851	\N	0013668	251512429	20260206	191026	전남87바4165	37.157995	127.383727	1	23.3	-23.3	0	NOUSE	\N	37.157995	127.383727	2026-02-06 10:15:14.08301+00	\N
852	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:15:14.08301+00	\N
853	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:15:14.08301+00	\N
854	\N	0013668	251509223	20260206	191508	전남87바4173	36.439658	128.211585	1	23.2	-23.2	0	NOUSE	\N	36.439658	128.211585	2026-02-06 10:15:14.08301+00	\N
855	\N	0013668	252228112	20260206	191012	전남87바4174	35.337948	126.796040	1	24.7	-24.7	0	NOUSE	\N	35.337948	126.79604	2026-02-06 10:15:14.08301+00	\N
856	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:15:14.08301+00	\N
857	\N	0013668	252214992	20260206	191012	전남87바4176	34.963896	127.612896	0	1.2	1.2	0	NOUSE	\N	34.963896	127.612896	2026-02-06 10:15:14.08301+00	\N
858	\N	0013668	239200586	20260206	191337	전남87바4177	36.291797	128.365400	0	6.7	6.7	0	NOUSE	\N	36.291797	128.3654	2026-02-06 10:15:14.08301+00	\N
859	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:15:14.08301+00	\N
860	\N	0013668	240074478	20260206	191105	전남87바4188	35.963548	127.103776	1	23.1	-23.1	0	NOUSE	\N	35.963548	127.103776	2026-02-06 10:15:14.08301+00	\N
861	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:15:14.08301+00	\N
862	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:15:14.108324+00	\N
863	\N	0013668	236275896	20260206	191326	전남87바1302	0.000000	0.000000	0	1.7	1.7	0	NOUSE	\N	0	0	2026-02-06 10:15:14.108324+00	\N
864	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:15:14.108324+00	\N
865	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:15:14.108324+00	\N
866	\N	0013668	252227307	20260206	191245	전남87바1305	35.372084	129.021760	0	4.2	4.2	0	NOUSE	\N	35.372084	129.02176	2026-02-06 10:15:14.108324+00	\N
867	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 10:15:14.108324+00	\N
868	\N	0013668	252713338	20260206	191435	전남87바1317	36.398799	127.356617	0	2.6	2.6	0	NOUSE	\N	36.398799	127.356617	2026-02-06 10:15:14.108324+00	\N
869	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:15:14.108324+00	\N
870	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:15:14.108324+00	\N
871	\N	0013668	249253808	20260206	191242	전남87바1325	36.590060	127.426664	1	22.5	-22.5	0	NOUSE	\N	36.59006	127.426664	2026-02-06 10:15:14.108324+00	\N
872	\N	0013668	252214998	20260206	191037	전남87바1326	35.386044	129.015808	1	11.9	-11.9	0	NOUSE	\N	35.386044	129.015808	2026-02-06 10:15:14.108324+00	\N
873	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:15:14.108324+00	\N
874	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:15:14.108324+00	\N
875	\N	0013668	251512431	20260206	190910	전남87바1351	37.248838	127.423753	1	25.1	-25.1	0	NOUSE	\N	37.248838	127.423753	2026-02-06 10:15:14.108324+00	\N
876	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:15:14.108324+00	\N
877	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:15:14.108324+00	\N
878	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:15:14.108324+00	\N
879	\N	0013668	236994200	20260206	191501	전남87바1362	36.388446	127.339464	0	1.7	1.7	0	2.8	2.8	36.388446	127.339464	2026-02-06 10:15:14.108324+00	\N
880	\N	0013668	252215001	20260206	191040	전남87바1364	37.086812	127.207872	0	3.5	3.5	0	NOUSE	\N	37.086812	127.207872	2026-02-06 10:15:14.108324+00	\N
881	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:15:14.108324+00	\N
882	\N	0013668	251512435	20260206	185643	전남87바1368	35.374363	128.831363	1	19.7	-19.7	0	0.2	0.2	35.374363	128.831363	2026-02-06 10:15:14.108324+00	\N
883	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:15:14.108324+00	\N
884	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:15:14.108324+00	\N
885	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:15:14.108324+00	\N
886	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:15:14.108324+00	\N
887	\N	0013668	235994979	20260206	191404	전남87바4157	35.460108	126.670968	0	5.4	5.4	0	NOUSE	\N	35.460108	126.670968	2026-02-06 10:15:14.108324+00	\N
888	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:15:14.108324+00	\N
889	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:15:14.108324+00	\N
890	\N	0013668	252799355	20260206	191442	전남87바4161	35.904960	128.492520	1	19.4	-19.4	0	NOUSE	\N	35.90496	128.49252	2026-02-06 10:15:14.108324+00	\N
891	\N	0013668	252227303	20260206	191222	전남87바4162	34.955180	126.502696	0	1.8	1.8	0	NOUSE	\N	34.95518	126.502696	2026-02-06 10:15:14.108324+00	\N
892	\N	0013668	251512429	20260206	191026	전남87바4165	37.157995	127.383727	1	23.3	-23.3	0	NOUSE	\N	37.157995	127.383727	2026-02-06 10:15:14.108324+00	\N
893	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:15:14.108324+00	\N
894	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:15:14.108324+00	\N
895	\N	0013668	251509223	20260206	191508	전남87바4173	36.439658	128.211585	1	23.2	-23.2	0	NOUSE	\N	36.439658	128.211585	2026-02-06 10:15:14.108324+00	\N
896	\N	0013668	252228112	20260206	191012	전남87바4174	35.337948	126.796040	1	24.7	-24.7	0	NOUSE	\N	35.337948	126.79604	2026-02-06 10:15:14.108324+00	\N
897	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:15:14.108324+00	\N
898	\N	0013668	252214992	20260206	191012	전남87바4176	34.963896	127.612896	0	1.2	1.2	0	NOUSE	\N	34.963896	127.612896	2026-02-06 10:15:14.108324+00	\N
899	\N	0013668	239200586	20260206	191337	전남87바4177	36.291797	128.365400	0	6.7	6.7	0	NOUSE	\N	36.291797	128.3654	2026-02-06 10:15:14.108324+00	\N
900	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:15:14.108324+00	\N
901	\N	0013668	240074478	20260206	191105	전남87바4188	35.963548	127.103776	1	23.1	-23.1	0	NOUSE	\N	35.963548	127.103776	2026-02-06 10:15:14.108324+00	\N
902	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:15:14.108324+00	\N
1352	\N	0013668	240074478	20260206	195105	전남87바4188	35.536488	126.813224	1	23.3	-23.3	0	NOUSE	\N	35.536488	126.813224	2026-02-06 10:52:02.909905+00	\N
1353	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:52:02.909905+00	\N
903	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:15:14.118999+00	\N
904	\N	0013668	236275896	20260206	191326	전남87바1302	0.000000	0.000000	0	1.7	1.7	0	NOUSE	\N	0	0	2026-02-06 10:15:14.118999+00	\N
905	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:15:14.118999+00	\N
906	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:15:14.118999+00	\N
907	\N	0013668	252227307	20260206	191245	전남87바1305	35.372084	129.021760	0	4.2	4.2	0	NOUSE	\N	35.372084	129.02176	2026-02-06 10:15:14.118999+00	\N
908	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 10:15:14.118999+00	\N
909	\N	0013668	252713338	20260206	191435	전남87바1317	36.398799	127.356617	0	2.6	2.6	0	NOUSE	\N	36.398799	127.356617	2026-02-06 10:15:14.118999+00	\N
910	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:15:14.118999+00	\N
911	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:15:14.118999+00	\N
912	\N	0013668	249253808	20260206	191242	전남87바1325	36.590060	127.426664	1	22.5	-22.5	0	NOUSE	\N	36.59006	127.426664	2026-02-06 10:15:14.118999+00	\N
913	\N	0013668	252214998	20260206	191037	전남87바1326	35.386044	129.015808	1	11.9	-11.9	0	NOUSE	\N	35.386044	129.015808	2026-02-06 10:15:14.118999+00	\N
914	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:15:14.118999+00	\N
915	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:15:14.118999+00	\N
916	\N	0013668	251512431	20260206	190910	전남87바1351	37.248838	127.423753	1	25.1	-25.1	0	NOUSE	\N	37.248838	127.423753	2026-02-06 10:15:14.118999+00	\N
917	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:15:14.118999+00	\N
918	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:15:14.118999+00	\N
919	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:15:14.118999+00	\N
920	\N	0013668	236994200	20260206	191501	전남87바1362	36.388446	127.339464	0	1.7	1.7	0	2.8	2.8	36.388446	127.339464	2026-02-06 10:15:14.118999+00	\N
921	\N	0013668	252215001	20260206	191040	전남87바1364	37.086812	127.207872	0	3.5	3.5	0	NOUSE	\N	37.086812	127.207872	2026-02-06 10:15:14.118999+00	\N
922	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:15:14.118999+00	\N
923	\N	0013668	251512435	20260206	185643	전남87바1368	35.374363	128.831363	1	19.7	-19.7	0	0.2	0.2	35.374363	128.831363	2026-02-06 10:15:14.118999+00	\N
924	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:15:14.118999+00	\N
925	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:15:14.118999+00	\N
926	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:15:14.118999+00	\N
927	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:15:14.118999+00	\N
928	\N	0013668	235994979	20260206	191404	전남87바4157	35.460108	126.670968	0	5.4	5.4	0	NOUSE	\N	35.460108	126.670968	2026-02-06 10:15:14.118999+00	\N
929	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:15:14.118999+00	\N
930	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:15:14.118999+00	\N
931	\N	0013668	252799355	20260206	191442	전남87바4161	35.904960	128.492520	1	19.4	-19.4	0	NOUSE	\N	35.90496	128.49252	2026-02-06 10:15:14.118999+00	\N
932	\N	0013668	252227303	20260206	191222	전남87바4162	34.955180	126.502696	0	1.8	1.8	0	NOUSE	\N	34.95518	126.502696	2026-02-06 10:15:14.118999+00	\N
933	\N	0013668	251512429	20260206	191026	전남87바4165	37.157995	127.383727	1	23.3	-23.3	0	NOUSE	\N	37.157995	127.383727	2026-02-06 10:15:14.118999+00	\N
934	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:15:14.118999+00	\N
935	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:15:14.118999+00	\N
936	\N	0013668	251509223	20260206	191508	전남87바4173	36.439658	128.211585	1	23.2	-23.2	0	NOUSE	\N	36.439658	128.211585	2026-02-06 10:15:14.118999+00	\N
937	\N	0013668	252228112	20260206	191012	전남87바4174	35.337948	126.796040	1	24.7	-24.7	0	NOUSE	\N	35.337948	126.79604	2026-02-06 10:15:14.118999+00	\N
938	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:15:14.118999+00	\N
939	\N	0013668	252214992	20260206	191012	전남87바4176	34.963896	127.612896	0	1.2	1.2	0	NOUSE	\N	34.963896	127.612896	2026-02-06 10:15:14.118999+00	\N
940	\N	0013668	239200586	20260206	191337	전남87바4177	36.291797	128.365400	0	6.7	6.7	0	NOUSE	\N	36.291797	128.3654	2026-02-06 10:15:14.118999+00	\N
941	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:15:14.118999+00	\N
942	\N	0013668	240074478	20260206	191105	전남87바4188	35.963548	127.103776	1	23.1	-23.1	0	NOUSE	\N	35.963548	127.103776	2026-02-06 10:15:14.118999+00	\N
943	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:15:14.118999+00	\N
944	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:15:14.140186+00	\N
945	\N	0013668	236275896	20260206	191326	전남87바1302	0.000000	0.000000	0	1.7	1.7	0	NOUSE	\N	0	0	2026-02-06 10:15:14.140186+00	\N
946	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:15:14.140186+00	\N
947	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:15:14.140186+00	\N
948	\N	0013668	252227307	20260206	191245	전남87바1305	35.372084	129.021760	0	4.2	4.2	0	NOUSE	\N	35.372084	129.02176	2026-02-06 10:15:14.140186+00	\N
949	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 10:15:14.140186+00	\N
950	\N	0013668	252713338	20260206	191435	전남87바1317	36.398799	127.356617	0	2.6	2.6	0	NOUSE	\N	36.398799	127.356617	2026-02-06 10:15:14.140186+00	\N
951	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:15:14.140186+00	\N
952	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:15:14.140186+00	\N
953	\N	0013668	249253808	20260206	191242	전남87바1325	36.590060	127.426664	1	22.5	-22.5	0	NOUSE	\N	36.59006	127.426664	2026-02-06 10:15:14.140186+00	\N
954	\N	0013668	252214998	20260206	191037	전남87바1326	35.386044	129.015808	1	11.9	-11.9	0	NOUSE	\N	35.386044	129.015808	2026-02-06 10:15:14.140186+00	\N
955	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:15:14.140186+00	\N
956	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:15:14.140186+00	\N
957	\N	0013668	251512431	20260206	190910	전남87바1351	37.248838	127.423753	1	25.1	-25.1	0	NOUSE	\N	37.248838	127.423753	2026-02-06 10:15:14.140186+00	\N
958	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:15:14.140186+00	\N
959	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:15:14.140186+00	\N
960	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:15:14.140186+00	\N
961	\N	0013668	236994200	20260206	191501	전남87바1362	36.388446	127.339464	0	1.7	1.7	0	2.8	2.8	36.388446	127.339464	2026-02-06 10:15:14.140186+00	\N
962	\N	0013668	252215001	20260206	191040	전남87바1364	37.086812	127.207872	0	3.5	3.5	0	NOUSE	\N	37.086812	127.207872	2026-02-06 10:15:14.140186+00	\N
963	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:15:14.140186+00	\N
964	\N	0013668	251512435	20260206	185643	전남87바1368	35.374363	128.831363	1	19.7	-19.7	0	0.2	0.2	35.374363	128.831363	2026-02-06 10:15:14.140186+00	\N
965	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:15:14.140186+00	\N
966	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:15:14.140186+00	\N
967	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:15:14.140186+00	\N
968	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:15:14.140186+00	\N
969	\N	0013668	235994979	20260206	191404	전남87바4157	35.460108	126.670968	0	5.4	5.4	0	NOUSE	\N	35.460108	126.670968	2026-02-06 10:15:14.140186+00	\N
970	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:15:14.140186+00	\N
971	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:15:14.140186+00	\N
972	\N	0013668	252799355	20260206	191442	전남87바4161	35.904960	128.492520	1	19.4	-19.4	0	NOUSE	\N	35.90496	128.49252	2026-02-06 10:15:14.140186+00	\N
973	\N	0013668	252227303	20260206	191222	전남87바4162	34.955180	126.502696	0	1.8	1.8	0	NOUSE	\N	34.95518	126.502696	2026-02-06 10:15:14.140186+00	\N
974	\N	0013668	251512429	20260206	191026	전남87바4165	37.157995	127.383727	1	23.3	-23.3	0	NOUSE	\N	37.157995	127.383727	2026-02-06 10:15:14.140186+00	\N
975	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:15:14.140186+00	\N
976	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:15:14.140186+00	\N
977	\N	0013668	251509223	20260206	191508	전남87바4173	36.439658	128.211585	1	23.2	-23.2	0	NOUSE	\N	36.439658	128.211585	2026-02-06 10:15:14.140186+00	\N
978	\N	0013668	252228112	20260206	191012	전남87바4174	35.337948	126.796040	1	24.7	-24.7	0	NOUSE	\N	35.337948	126.79604	2026-02-06 10:15:14.140186+00	\N
979	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:15:14.140186+00	\N
980	\N	0013668	252214992	20260206	191012	전남87바4176	34.963896	127.612896	0	1.2	1.2	0	NOUSE	\N	34.963896	127.612896	2026-02-06 10:15:14.140186+00	\N
981	\N	0013668	239200586	20260206	191337	전남87바4177	36.291797	128.365400	0	6.7	6.7	0	NOUSE	\N	36.291797	128.3654	2026-02-06 10:15:14.140186+00	\N
982	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:15:14.140186+00	\N
983	\N	0013668	240074478	20260206	191105	전남87바4188	35.963548	127.103776	1	23.1	-23.1	0	NOUSE	\N	35.963548	127.103776	2026-02-06 10:15:14.140186+00	\N
984	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:15:14.140186+00	\N
985	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:25:14.139011+00	\N
986	\N	0013668	236275896	20260206	192326	전남87바1302	0.000000	0.000000	0	1.6	1.6	0	NOUSE	\N	0	0	2026-02-06 10:25:14.139011+00	\N
987	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:25:14.139011+00	\N
988	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:25:14.139011+00	\N
989	\N	0013668	252227307	20260206	192245	전남87바1305	35.373352	129.018232	0	0.7	0.7	0	NOUSE	\N	35.373352	129.018232	2026-02-06 10:25:14.139011+00	\N
990	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 10:25:14.139011+00	\N
991	\N	0013668	252713338	20260206	192439	전남87바1317	36.425206	127.417650	0	2.7	2.7	0	NOUSE	\N	36.425206	127.41765	2026-02-06 10:25:14.139011+00	\N
992	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:25:14.139011+00	\N
993	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:25:14.139011+00	\N
994	\N	0013668	249253808	20260206	192242	전남87바1325	36.711036	127.439392	1	22.2	-22.2	0	NOUSE	\N	36.711036	127.439392	2026-02-06 10:25:14.139011+00	\N
995	\N	0013668	252214998	20260206	192037	전남87바1326	35.387256	129.014544	1	10.6	-10.6	0	NOUSE	\N	35.387256	129.014544	2026-02-06 10:25:14.139011+00	\N
996	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:25:14.139011+00	\N
997	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:25:14.139011+00	\N
999	\N	0013668	251512431	20260206	190910	전남87바1351	37.248838	127.423753	1	25.1	-25.1	0	NOUSE	\N	37.248838	127.423753	2026-02-06 10:25:14.139011+00	\N
1000	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:25:14.139011+00	\N
1001	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:25:14.139011+00	\N
998	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:25:14.139636+00	\N
1003	\N	0013668	236275896	20260206	192326	전남87바1302	0.000000	0.000000	0	1.6	1.6	0	NOUSE	\N	0	0	2026-02-06 10:25:14.139636+00	\N
1004	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:25:14.139636+00	\N
1005	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:25:14.139636+00	\N
1006	\N	0013668	252227307	20260206	192245	전남87바1305	35.373352	129.018232	0	0.7	0.7	0	NOUSE	\N	35.373352	129.018232	2026-02-06 10:25:14.139636+00	\N
1007	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 10:25:14.139636+00	\N
1008	\N	0013668	252713338	20260206	192439	전남87바1317	36.425206	127.417650	0	2.7	2.7	0	NOUSE	\N	36.425206	127.41765	2026-02-06 10:25:14.139636+00	\N
1009	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:25:14.139636+00	\N
1010	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:25:14.139636+00	\N
1011	\N	0013668	249253808	20260206	192242	전남87바1325	36.711036	127.439392	1	22.2	-22.2	0	NOUSE	\N	36.711036	127.439392	2026-02-06 10:25:14.139636+00	\N
1012	\N	0013668	252214998	20260206	192037	전남87바1326	35.387256	129.014544	1	10.6	-10.6	0	NOUSE	\N	35.387256	129.014544	2026-02-06 10:25:14.139636+00	\N
1002	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:25:14.139011+00	\N
1013	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:25:14.139636+00	\N
1014	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:25:14.139636+00	\N
1015	\N	0013668	236994200	20260206	192504	전남87바1362	36.298813	127.313984	0	1.6	1.6	0	2.8	2.8	36.298813	127.313984	2026-02-06 10:25:14.139011+00	\N
1016	\N	0013668	251512431	20260206	190910	전남87바1351	37.248838	127.423753	1	25.1	-25.1	0	NOUSE	\N	37.248838	127.423753	2026-02-06 10:25:14.139636+00	\N
1017	\N	0013668	252215001	20260206	191540	전남87바1364	37.087188	127.216976	0	3.7	3.7	0	NOUSE	\N	37.087188	127.216976	2026-02-06 10:25:14.139011+00	\N
1018	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:25:14.139636+00	\N
1019	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:25:14.139011+00	\N
1020	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:25:14.139636+00	\N
1021	\N	0013668	251512435	20260206	185643	전남87바1368	35.374363	128.831363	1	19.7	-19.7	0	0.2	0.2	35.374363	128.831363	2026-02-06 10:25:14.139011+00	\N
1022	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:25:14.139636+00	\N
1023	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:25:14.139011+00	\N
1024	\N	0013668	236994200	20260206	192504	전남87바1362	36.298813	127.313984	0	1.6	1.6	0	2.8	2.8	36.298813	127.313984	2026-02-06 10:25:14.139636+00	\N
1025	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:25:14.139011+00	\N
1026	\N	0013668	252215001	20260206	191540	전남87바1364	37.087188	127.216976	0	3.7	3.7	0	NOUSE	\N	37.087188	127.216976	2026-02-06 10:25:14.139636+00	\N
1027	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:25:14.139011+00	\N
1028	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:25:14.139636+00	\N
1029	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:25:14.139011+00	\N
1030	\N	0013668	251512435	20260206	185643	전남87바1368	35.374363	128.831363	1	19.7	-19.7	0	0.2	0.2	35.374363	128.831363	2026-02-06 10:25:14.139636+00	\N
1031	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:25:14.139636+00	\N
1032	\N	0013668	235994979	20260206	192404	전남87바4157	35.587816	126.697616	0	5.4	5.4	0	NOUSE	\N	35.587816	126.697616	2026-02-06 10:25:14.139011+00	\N
1033	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:25:14.139636+00	\N
1034	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:25:14.139011+00	\N
1035	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:25:14.139636+00	\N
1036	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:25:14.139011+00	\N
1037	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:25:14.139636+00	\N
1038	\N	0013668	252799355	20260206	192442	전남87바4161	35.916784	128.634488	1	21.5	-21.5	0	NOUSE	\N	35.916784	128.634488	2026-02-06 10:25:14.139011+00	\N
1039	\N	0013668	235994979	20260206	192404	전남87바4157	35.587816	126.697616	0	5.4	5.4	0	NOUSE	\N	35.587816	126.697616	2026-02-06 10:25:14.139636+00	\N
1040	\N	0013668	252227303	20260206	192222	전남87바4162	35.085436	126.480784	0	2.2	2.2	0	NOUSE	\N	35.085436	126.480784	2026-02-06 10:25:14.139011+00	\N
1041	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:25:14.139636+00	\N
1042	\N	0013668	251512429	20260206	191528	전남87바4165	37.147991	127.384745	1	21.8	-21.8	0	NOUSE	\N	37.147991	127.384745	2026-02-06 10:25:14.139011+00	\N
1043	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:25:14.139636+00	\N
1044	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:25:14.139011+00	\N
1046	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:25:14.139011+00	\N
1047	\N	0013668	251509223	20260206	192512	전남87바4173	36.340141	128.223310	1	19.8	-19.8	0	NOUSE	\N	36.340141	128.22331	2026-02-06 10:25:14.139011+00	\N
1048	\N	0013668	252228112	20260206	192012	전남87바4174	35.320380	126.754328	1	21.1	-21.1	0	NOUSE	\N	35.32038	126.754328	2026-02-06 10:25:14.139011+00	\N
1049	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:25:14.139011+00	\N
1050	\N	0013668	252214992	20260206	192012	전남87바4176	35.003140	127.484792	0	2.5	2.5	0	NOUSE	\N	35.00314	127.484792	2026-02-06 10:25:14.139011+00	\N
1051	\N	0013668	239200586	20260206	192341	전남87바4177	36.372121	128.257286	0	3.7	3.7	0	NOUSE	\N	36.372121	128.257286	2026-02-06 10:25:14.139011+00	\N
1052	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:25:14.139011+00	\N
1053	\N	0013668	240074478	20260206	192105	전남87바4188	35.849112	127.048568	1	22.3	-22.3	0	NOUSE	\N	35.849112	127.048568	2026-02-06 10:25:14.139011+00	\N
1054	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:25:14.139011+00	\N
1354	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:52:02.936046+00	\N
1355	\N	0013668	236275896	20260206	194826	전남87바1302	35.168472	126.781480	0	1.3	1.3	0	NOUSE	\N	35.168472	126.78148	2026-02-06 10:52:02.936046+00	\N
1356	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:52:02.936046+00	\N
1357	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:52:02.936046+00	\N
1358	\N	0013668	252227307	20260206	194745	전남87바1305	35.530112	129.107760	0	2.8	2.8	0	NOUSE	\N	35.530112	129.10776	2026-02-06 10:52:02.936046+00	\N
1359	\N	0013668	252214997	20260206	194916	전남87바1313	37.266500	127.499336	1	18.6	-18.6	0	NOUSE	\N	37.2665	127.499336	2026-02-06 10:52:02.936046+00	\N
1360	\N	0013668	252713338	20260206	194948	전남87바1317	36.687862	127.425547	0	2.7	2.7	0	NOUSE	\N	36.687862	127.425547	2026-02-06 10:52:02.936046+00	\N
1361	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:52:02.936046+00	\N
1362	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:52:02.936046+00	\N
1363	\N	0013668	249253808	20260206	194742	전남87바1325	36.984048	127.471768	1	20.4	-20.4	0	NOUSE	\N	36.984048	127.471768	2026-02-06 10:52:02.936046+00	\N
1364	\N	0013668	252214998	20260206	195037	전남87바1326	35.273656	128.973832	1	19.8	-19.8	1	1.3	-1.3	35.273656	128.973832	2026-02-06 10:52:02.936046+00	\N
1365	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:52:02.936046+00	\N
1366	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:52:02.936046+00	\N
1367	\N	0013668	251512431	20260206	190910	전남87바1351	37.248838	127.423753	1	25.1	-25.1	0	NOUSE	\N	37.248838	127.423753	2026-02-06 10:52:02.936046+00	\N
1368	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:52:02.936046+00	\N
1369	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:52:02.936046+00	\N
1370	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:52:02.936046+00	\N
1371	\N	0013668	236994200	20260206	195013	전남87바1362	36.085836	127.104505	0	1.8	1.8	0	2.9	2.9	36.085836	127.104505	2026-02-06 10:52:02.936046+00	\N
1372	\N	0013668	252215001	20260206	191540	전남87바1364	37.087188	127.216976	0	3.7	3.7	0	NOUSE	\N	37.087188	127.216976	2026-02-06 10:52:02.936046+00	\N
1373	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:52:02.936046+00	\N
1374	\N	0013668	251512435	20260206	194914	전남87바1368	35.258302	128.825201	1	18.8	-18.8	0	5.0	5	35.258302	128.825201	2026-02-06 10:52:02.936046+00	\N
1375	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:52:02.936046+00	\N
1376	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:52:02.936046+00	\N
1377	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:52:02.936046+00	\N
1378	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:52:02.936046+00	\N
1379	\N	0013668	235994979	20260206	194904	전남87바4157	35.671572	126.733704	0	5.2	5.2	0	NOUSE	\N	35.671572	126.733704	2026-02-06 10:52:02.936046+00	\N
1380	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:52:02.936046+00	\N
1381	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:52:02.936046+00	\N
1382	\N	0013668	252799355	20260206	194942	전남87바4161	35.656756	128.745792	1	19.6	-19.6	0	NOUSE	\N	35.656756	128.745792	2026-02-06 10:52:02.936046+00	\N
1383	\N	0013668	252227303	20260206	194722	전남87바4162	35.384144	126.612832	0	2.7	2.7	0	NOUSE	\N	35.384144	126.612832	2026-02-06 10:52:02.936046+00	\N
1384	\N	0013668	251512429	20260206	191528	전남87바4165	37.147991	127.384745	1	21.8	-21.8	0	NOUSE	\N	37.147991	127.384745	2026-02-06 10:52:02.936046+00	\N
1385	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:52:02.936046+00	\N
1386	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:52:02.936046+00	\N
1387	\N	0013668	251509223	20260206	195021	전남87바4173	36.107702	128.361054	1	19.7	-19.7	0	NOUSE	\N	36.107702	128.361054	2026-02-06 10:52:02.936046+00	\N
1388	\N	0013668	252228112	20260206	192012	전남87바4174	35.320380	126.754328	1	21.1	-21.1	0	NOUSE	\N	35.32038	126.754328	2026-02-06 10:52:02.936046+00	\N
1389	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:52:02.936046+00	\N
1390	\N	0013668	252214992	20260206	195012	전남87바4176	35.210612	127.235072	0	2.6	2.6	0	NOUSE	\N	35.210612	127.235072	2026-02-06 10:52:02.936046+00	\N
1067	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:25:14.205916+00	\N
1068	\N	0013668	236275896	20260206	192326	전남87바1302	0.000000	0.000000	0	1.6	1.6	0	NOUSE	\N	0	0	2026-02-06 10:25:14.205916+00	\N
1069	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:25:14.205916+00	\N
1070	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:25:14.205916+00	\N
1071	\N	0013668	252227307	20260206	192245	전남87바1305	35.373352	129.018232	0	0.7	0.7	0	NOUSE	\N	35.373352	129.018232	2026-02-06 10:25:14.205916+00	\N
1072	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 10:25:14.205916+00	\N
1073	\N	0013668	252713338	20260206	192439	전남87바1317	36.425206	127.417650	0	2.7	2.7	0	NOUSE	\N	36.425206	127.41765	2026-02-06 10:25:14.205916+00	\N
1074	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:25:14.205916+00	\N
1075	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:25:14.205916+00	\N
1076	\N	0013668	249253808	20260206	192242	전남87바1325	36.711036	127.439392	1	22.2	-22.2	0	NOUSE	\N	36.711036	127.439392	2026-02-06 10:25:14.205916+00	\N
1077	\N	0013668	252214998	20260206	192037	전남87바1326	35.387256	129.014544	1	10.6	-10.6	0	NOUSE	\N	35.387256	129.014544	2026-02-06 10:25:14.205916+00	\N
1078	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:25:14.205916+00	\N
1079	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:25:14.205916+00	\N
1080	\N	0013668	251512431	20260206	190910	전남87바1351	37.248838	127.423753	1	25.1	-25.1	0	NOUSE	\N	37.248838	127.423753	2026-02-06 10:25:14.205916+00	\N
1081	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:25:14.205916+00	\N
1082	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:25:14.205916+00	\N
1083	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:25:14.205916+00	\N
1084	\N	0013668	236994200	20260206	192504	전남87바1362	36.298813	127.313984	0	1.6	1.6	0	2.8	2.8	36.298813	127.313984	2026-02-06 10:25:14.205916+00	\N
1085	\N	0013668	252215001	20260206	191540	전남87바1364	37.087188	127.216976	0	3.7	3.7	0	NOUSE	\N	37.087188	127.216976	2026-02-06 10:25:14.205916+00	\N
1086	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:25:14.205916+00	\N
1087	\N	0013668	251512435	20260206	185643	전남87바1368	35.374363	128.831363	1	19.7	-19.7	0	0.2	0.2	35.374363	128.831363	2026-02-06 10:25:14.205916+00	\N
1088	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:25:14.205916+00	\N
1089	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:25:14.205916+00	\N
1090	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:25:14.205916+00	\N
1091	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:25:14.205916+00	\N
1092	\N	0013668	235994979	20260206	192404	전남87바4157	35.587816	126.697616	0	5.4	5.4	0	NOUSE	\N	35.587816	126.697616	2026-02-06 10:25:14.205916+00	\N
1093	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:25:14.205916+00	\N
1094	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:25:14.205916+00	\N
1095	\N	0013668	252799355	20260206	192442	전남87바4161	35.916784	128.634488	1	21.5	-21.5	0	NOUSE	\N	35.916784	128.634488	2026-02-06 10:25:14.205916+00	\N
1096	\N	0013668	252227303	20260206	192222	전남87바4162	35.085436	126.480784	0	2.2	2.2	0	NOUSE	\N	35.085436	126.480784	2026-02-06 10:25:14.205916+00	\N
1097	\N	0013668	251512429	20260206	191528	전남87바4165	37.147991	127.384745	1	21.8	-21.8	0	NOUSE	\N	37.147991	127.384745	2026-02-06 10:25:14.205916+00	\N
1098	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:25:14.205916+00	\N
1099	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:25:14.205916+00	\N
1100	\N	0013668	251509223	20260206	192512	전남87바4173	36.340141	128.223310	1	19.8	-19.8	0	NOUSE	\N	36.340141	128.22331	2026-02-06 10:25:14.205916+00	\N
1101	\N	0013668	252228112	20260206	192012	전남87바4174	35.320380	126.754328	1	21.1	-21.1	0	NOUSE	\N	35.32038	126.754328	2026-02-06 10:25:14.205916+00	\N
1102	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:25:14.205916+00	\N
1103	\N	0013668	252214992	20260206	192012	전남87바4176	35.003140	127.484792	0	2.5	2.5	0	NOUSE	\N	35.00314	127.484792	2026-02-06 10:25:14.205916+00	\N
1104	\N	0013668	239200586	20260206	192341	전남87바4177	36.372121	128.257286	0	3.7	3.7	0	NOUSE	\N	36.372121	128.257286	2026-02-06 10:25:14.205916+00	\N
1105	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:25:14.205916+00	\N
1106	\N	0013668	240074478	20260206	192105	전남87바4188	35.849112	127.048568	1	22.3	-22.3	0	NOUSE	\N	35.849112	127.048568	2026-02-06 10:25:14.205916+00	\N
1107	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:25:14.205916+00	\N
1391	\N	0013668	239200586	20260206	194850	전남87바4177	36.619811	128.152410	0	5.8	5.8	0	NOUSE	\N	36.619811	128.15241	2026-02-06 10:52:02.936046+00	\N
1392	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:52:02.936046+00	\N
1393	\N	0013668	240074478	20260206	195105	전남87바4188	35.536488	126.813224	1	23.3	-23.3	0	NOUSE	\N	35.536488	126.813224	2026-02-06 10:52:02.936046+00	\N
1394	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:52:02.936046+00	\N
1108	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:25:14.219972+00	\N
1109	\N	0013668	236275896	20260206	192326	전남87바1302	0.000000	0.000000	0	1.6	1.6	0	NOUSE	\N	0	0	2026-02-06 10:25:14.219972+00	\N
1110	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:25:14.219972+00	\N
1111	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:25:14.219972+00	\N
1112	\N	0013668	252227307	20260206	192245	전남87바1305	35.373352	129.018232	0	0.7	0.7	0	NOUSE	\N	35.373352	129.018232	2026-02-06 10:25:14.219972+00	\N
1113	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 10:25:14.219972+00	\N
1114	\N	0013668	252713338	20260206	192439	전남87바1317	36.425206	127.417650	0	2.7	2.7	0	NOUSE	\N	36.425206	127.41765	2026-02-06 10:25:14.219972+00	\N
1115	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:25:14.219972+00	\N
1116	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:25:14.219972+00	\N
1117	\N	0013668	249253808	20260206	192242	전남87바1325	36.711036	127.439392	1	22.2	-22.2	0	NOUSE	\N	36.711036	127.439392	2026-02-06 10:25:14.219972+00	\N
1118	\N	0013668	252214998	20260206	192037	전남87바1326	35.387256	129.014544	1	10.6	-10.6	0	NOUSE	\N	35.387256	129.014544	2026-02-06 10:25:14.219972+00	\N
1119	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:25:14.219972+00	\N
1120	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:25:14.219972+00	\N
1121	\N	0013668	251512431	20260206	190910	전남87바1351	37.248838	127.423753	1	25.1	-25.1	0	NOUSE	\N	37.248838	127.423753	2026-02-06 10:25:14.219972+00	\N
1122	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:25:14.219972+00	\N
1123	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:25:14.219972+00	\N
1124	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:25:14.219972+00	\N
1125	\N	0013668	236994200	20260206	192504	전남87바1362	36.298813	127.313984	0	1.6	1.6	0	2.8	2.8	36.298813	127.313984	2026-02-06 10:25:14.219972+00	\N
1126	\N	0013668	252215001	20260206	191540	전남87바1364	37.087188	127.216976	0	3.7	3.7	0	NOUSE	\N	37.087188	127.216976	2026-02-06 10:25:14.219972+00	\N
1127	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:25:14.219972+00	\N
1128	\N	0013668	251512435	20260206	185643	전남87바1368	35.374363	128.831363	1	19.7	-19.7	0	0.2	0.2	35.374363	128.831363	2026-02-06 10:25:14.219972+00	\N
1129	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:25:14.219972+00	\N
1130	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:25:14.219972+00	\N
1131	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:25:14.219972+00	\N
1132	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:25:14.219972+00	\N
1133	\N	0013668	235994979	20260206	192404	전남87바4157	35.587816	126.697616	0	5.4	5.4	0	NOUSE	\N	35.587816	126.697616	2026-02-06 10:25:14.219972+00	\N
1134	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:25:14.219972+00	\N
1135	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:25:14.219972+00	\N
1136	\N	0013668	252799355	20260206	192442	전남87바4161	35.916784	128.634488	1	21.5	-21.5	0	NOUSE	\N	35.916784	128.634488	2026-02-06 10:25:14.219972+00	\N
1137	\N	0013668	252227303	20260206	192222	전남87바4162	35.085436	126.480784	0	2.2	2.2	0	NOUSE	\N	35.085436	126.480784	2026-02-06 10:25:14.219972+00	\N
1138	\N	0013668	251512429	20260206	191528	전남87바4165	37.147991	127.384745	1	21.8	-21.8	0	NOUSE	\N	37.147991	127.384745	2026-02-06 10:25:14.219972+00	\N
1139	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:25:14.219972+00	\N
1140	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:25:14.219972+00	\N
1141	\N	0013668	251509223	20260206	192512	전남87바4173	36.340141	128.223310	1	19.8	-19.8	0	NOUSE	\N	36.340141	128.22331	2026-02-06 10:25:14.219972+00	\N
1142	\N	0013668	252228112	20260206	192012	전남87바4174	35.320380	126.754328	1	21.1	-21.1	0	NOUSE	\N	35.32038	126.754328	2026-02-06 10:25:14.219972+00	\N
1143	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:25:14.219972+00	\N
1144	\N	0013668	252214992	20260206	192012	전남87바4176	35.003140	127.484792	0	2.5	2.5	0	NOUSE	\N	35.00314	127.484792	2026-02-06 10:25:14.219972+00	\N
1145	\N	0013668	239200586	20260206	192341	전남87바4177	36.372121	128.257286	0	3.7	3.7	0	NOUSE	\N	36.372121	128.257286	2026-02-06 10:25:14.219972+00	\N
1146	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:25:14.219972+00	\N
1147	\N	0013668	240074478	20260206	192105	전남87바4188	35.849112	127.048568	1	22.3	-22.3	0	NOUSE	\N	35.849112	127.048568	2026-02-06 10:25:14.219972+00	\N
1148	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:25:14.219972+00	\N
1395	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:52:02.949046+00	\N
1396	\N	0013668	236275896	20260206	194826	전남87바1302	35.168472	126.781480	0	1.3	1.3	0	NOUSE	\N	35.168472	126.78148	2026-02-06 10:52:02.949046+00	\N
1397	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:52:02.949046+00	\N
1398	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:52:02.949046+00	\N
1399	\N	0013668	252227307	20260206	194745	전남87바1305	35.530112	129.107760	0	2.8	2.8	0	NOUSE	\N	35.530112	129.10776	2026-02-06 10:52:02.949046+00	\N
1400	\N	0013668	252214997	20260206	194916	전남87바1313	37.266500	127.499336	1	18.6	-18.6	0	NOUSE	\N	37.2665	127.499336	2026-02-06 10:52:02.949046+00	\N
1149	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:35:14.131622+00	\N
1150	\N	0013668	236275896	20260206	193326	전남87바1302	0.000000	0.000000	0	1.5	1.5	0	NOUSE	\N	0	0	2026-02-06 10:35:14.131622+00	\N
1151	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:35:14.131622+00	\N
1152	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:35:14.131622+00	\N
1153	\N	0013668	252227307	20260206	193245	전남87바1305	35.375648	129.046920	0	2.1	2.1	0	NOUSE	\N	35.375648	129.04692	2026-02-06 10:35:14.131622+00	\N
1154	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 10:35:14.131622+00	\N
1155	\N	0013668	252713338	20260206	193442	전남87바1317	36.504026	127.429265	0	2.7	2.7	0	NOUSE	\N	36.504026	127.429265	2026-02-06 10:35:14.131622+00	\N
1156	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:35:14.131622+00	\N
1157	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:35:14.131622+00	\N
1158	\N	0013668	249253808	20260206	193242	전남87바1325	36.808644	127.497856	1	18.9	-18.9	0	NOUSE	\N	36.808644	127.497856	2026-02-06 10:35:14.131622+00	\N
1159	\N	0013668	252214998	20260206	193037	전남87바1326	35.378304	129.025776	1	19.2	-19.2	0	2.7	2.7	35.378304	129.025776	2026-02-06 10:35:14.131622+00	\N
1160	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:35:14.131622+00	\N
1161	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:35:14.131622+00	\N
1162	\N	0013668	251512431	20260206	190910	전남87바1351	37.248838	127.423753	1	25.1	-25.1	0	NOUSE	\N	37.248838	127.423753	2026-02-06 10:35:14.131622+00	\N
1163	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:35:14.131622+00	\N
1164	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:35:14.131622+00	\N
1165	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:35:14.131622+00	\N
1166	\N	0013668	236994200	20260206	193508	전남87바1362	36.198703	127.263804	0	1.6	1.6	0	2.8	2.8	36.198703	127.263804	2026-02-06 10:35:14.131622+00	\N
1167	\N	0013668	252215001	20260206	191540	전남87바1364	37.087188	127.216976	0	3.7	3.7	0	NOUSE	\N	37.087188	127.216976	2026-02-06 10:35:14.131622+00	\N
1168	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:35:14.131622+00	\N
1169	\N	0013668	251512435	20260206	193413	전남87바1368	35.258326	128.825275	1	18.6	-18.6	0	3.8	3.8	35.258326	128.825275	2026-02-06 10:35:14.131622+00	\N
1170	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:35:14.131622+00	\N
1171	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:35:14.131622+00	\N
1172	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:35:14.131622+00	\N
1173	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:35:14.131622+00	\N
1174	\N	0013668	235994979	20260206	193404	전남87바4157	35.671568	126.733696	0	5.2	5.2	0	NOUSE	\N	35.671568	126.733696	2026-02-06 10:35:14.131622+00	\N
1175	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:35:14.131622+00	\N
1176	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:35:14.131622+00	\N
1177	\N	0013668	252799355	20260206	193442	전남87바4161	35.831236	128.699720	1	22.9	-22.9	0	NOUSE	\N	35.831236	128.69972	2026-02-06 10:35:14.131622+00	\N
1178	\N	0013668	252227303	20260206	193222	전남87바4162	35.216224	126.490504	0	2.3	2.3	0	NOUSE	\N	35.216224	126.490504	2026-02-06 10:35:14.131622+00	\N
1179	\N	0013668	251512429	20260206	191528	전남87바4165	37.147991	127.384745	1	21.8	-21.8	0	NOUSE	\N	37.147991	127.384745	2026-02-06 10:35:14.131622+00	\N
1180	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:35:14.131622+00	\N
1181	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:35:14.131622+00	\N
1182	\N	0013668	251509223	20260206	193014	전남87바4173	36.290260	128.229825	1	20.8	-20.8	0	NOUSE	\N	36.29026	128.229825	2026-02-06 10:35:14.131622+00	\N
1183	\N	0013668	252228112	20260206	192012	전남87바4174	35.320380	126.754328	1	21.1	-21.1	0	NOUSE	\N	35.32038	126.754328	2026-02-06 10:35:14.131622+00	\N
1184	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:35:14.131622+00	\N
1185	\N	0013668	252214992	20260206	193012	전남87바4176	35.018476	127.358632	0	3.1	3.1	0	NOUSE	\N	35.018476	127.358632	2026-02-06 10:35:14.131622+00	\N
1186	\N	0013668	239200586	20260206	193344	전남87바4177	36.472043	128.201202	0	5.2	5.2	0	NOUSE	\N	36.472043	128.201202	2026-02-06 10:35:14.131622+00	\N
1187	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:35:14.131622+00	\N
1188	\N	0013668	240074478	20260206	193105	전남87바4188	35.736268	126.988528	1	21.5	-21.5	0	NOUSE	\N	35.736268	126.988528	2026-02-06 10:35:14.131622+00	\N
1189	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:35:14.131622+00	\N
1401	\N	0013668	252713338	20260206	194948	전남87바1317	36.687862	127.425547	0	2.7	2.7	0	NOUSE	\N	36.687862	127.425547	2026-02-06 10:52:02.949046+00	\N
1402	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:52:02.949046+00	\N
1403	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:52:02.949046+00	\N
1404	\N	0013668	249253808	20260206	194742	전남87바1325	36.984048	127.471768	1	20.4	-20.4	0	NOUSE	\N	36.984048	127.471768	2026-02-06 10:52:02.949046+00	\N
1405	\N	0013668	252214998	20260206	195037	전남87바1326	35.273656	128.973832	1	19.8	-19.8	1	1.3	-1.3	35.273656	128.973832	2026-02-06 10:52:02.949046+00	\N
1406	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:52:02.949046+00	\N
1190	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:35:14.187791+00	\N
1191	\N	0013668	236275896	20260206	193326	전남87바1302	0.000000	0.000000	0	1.5	1.5	0	NOUSE	\N	0	0	2026-02-06 10:35:14.187791+00	\N
1192	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:35:14.187791+00	\N
1193	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:35:14.187791+00	\N
1194	\N	0013668	252227307	20260206	193245	전남87바1305	35.375648	129.046920	0	2.1	2.1	0	NOUSE	\N	35.375648	129.04692	2026-02-06 10:35:14.187791+00	\N
1195	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 10:35:14.187791+00	\N
1196	\N	0013668	252713338	20260206	193442	전남87바1317	36.504026	127.429265	0	2.7	2.7	0	NOUSE	\N	36.504026	127.429265	2026-02-06 10:35:14.187791+00	\N
1197	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:35:14.187791+00	\N
1198	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:35:14.187791+00	\N
1199	\N	0013668	249253808	20260206	193242	전남87바1325	36.808644	127.497856	1	18.9	-18.9	0	NOUSE	\N	36.808644	127.497856	2026-02-06 10:35:14.187791+00	\N
1200	\N	0013668	252214998	20260206	193037	전남87바1326	35.378304	129.025776	1	19.2	-19.2	0	2.7	2.7	35.378304	129.025776	2026-02-06 10:35:14.187791+00	\N
1201	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:35:14.187791+00	\N
1202	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:35:14.187791+00	\N
1203	\N	0013668	251512431	20260206	190910	전남87바1351	37.248838	127.423753	1	25.1	-25.1	0	NOUSE	\N	37.248838	127.423753	2026-02-06 10:35:14.187791+00	\N
1204	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:35:14.187791+00	\N
1205	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:35:14.187791+00	\N
1206	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:35:14.187791+00	\N
1207	\N	0013668	236994200	20260206	193508	전남87바1362	36.198703	127.263804	0	1.6	1.6	0	2.8	2.8	36.198703	127.263804	2026-02-06 10:35:14.187791+00	\N
1208	\N	0013668	252215001	20260206	191540	전남87바1364	37.087188	127.216976	0	3.7	3.7	0	NOUSE	\N	37.087188	127.216976	2026-02-06 10:35:14.187791+00	\N
1209	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:35:14.187791+00	\N
1210	\N	0013668	251512435	20260206	193413	전남87바1368	35.258326	128.825275	1	18.6	-18.6	0	3.8	3.8	35.258326	128.825275	2026-02-06 10:35:14.187791+00	\N
1211	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:35:14.187791+00	\N
1212	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:35:14.187791+00	\N
1213	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:35:14.187791+00	\N
1214	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:35:14.187791+00	\N
1215	\N	0013668	235994979	20260206	193404	전남87바4157	35.671568	126.733696	0	5.2	5.2	0	NOUSE	\N	35.671568	126.733696	2026-02-06 10:35:14.187791+00	\N
1216	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:35:14.187791+00	\N
1217	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:35:14.187791+00	\N
1218	\N	0013668	252799355	20260206	193442	전남87바4161	35.831236	128.699720	1	22.9	-22.9	0	NOUSE	\N	35.831236	128.69972	2026-02-06 10:35:14.187791+00	\N
1219	\N	0013668	252227303	20260206	193222	전남87바4162	35.216224	126.490504	0	2.3	2.3	0	NOUSE	\N	35.216224	126.490504	2026-02-06 10:35:14.187791+00	\N
1220	\N	0013668	251512429	20260206	191528	전남87바4165	37.147991	127.384745	1	21.8	-21.8	0	NOUSE	\N	37.147991	127.384745	2026-02-06 10:35:14.187791+00	\N
1221	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:35:14.187791+00	\N
1222	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:35:14.187791+00	\N
1223	\N	0013668	251509223	20260206	193014	전남87바4173	36.290260	128.229825	1	20.8	-20.8	0	NOUSE	\N	36.29026	128.229825	2026-02-06 10:35:14.187791+00	\N
1224	\N	0013668	252228112	20260206	192012	전남87바4174	35.320380	126.754328	1	21.1	-21.1	0	NOUSE	\N	35.32038	126.754328	2026-02-06 10:35:14.187791+00	\N
1225	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:35:14.187791+00	\N
1226	\N	0013668	252214992	20260206	193012	전남87바4176	35.018476	127.358632	0	3.1	3.1	0	NOUSE	\N	35.018476	127.358632	2026-02-06 10:35:14.187791+00	\N
1227	\N	0013668	239200586	20260206	193344	전남87바4177	36.472043	128.201202	0	5.2	5.2	0	NOUSE	\N	36.472043	128.201202	2026-02-06 10:35:14.187791+00	\N
1228	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:35:14.187791+00	\N
1229	\N	0013668	240074478	20260206	193105	전남87바4188	35.736268	126.988528	1	21.5	-21.5	0	NOUSE	\N	35.736268	126.988528	2026-02-06 10:35:14.187791+00	\N
1230	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:35:14.187791+00	\N
1407	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:52:02.949046+00	\N
1408	\N	0013668	251512431	20260206	190910	전남87바1351	37.248838	127.423753	1	25.1	-25.1	0	NOUSE	\N	37.248838	127.423753	2026-02-06 10:52:02.949046+00	\N
1409	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:52:02.949046+00	\N
1410	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:52:02.949046+00	\N
1411	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:52:02.949046+00	\N
1412	\N	0013668	236994200	20260206	195013	전남87바1362	36.085836	127.104505	0	1.8	1.8	0	2.9	2.9	36.085836	127.104505	2026-02-06 10:52:02.949046+00	\N
1231	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:35:14.136385+00	\N
1232	\N	0013668	236275896	20260206	193326	전남87바1302	0.000000	0.000000	0	1.5	1.5	0	NOUSE	\N	0	0	2026-02-06 10:35:14.136385+00	\N
1233	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:35:14.136385+00	\N
1234	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:35:14.136385+00	\N
1235	\N	0013668	252227307	20260206	193245	전남87바1305	35.375648	129.046920	0	2.1	2.1	0	NOUSE	\N	35.375648	129.04692	2026-02-06 10:35:14.136385+00	\N
1236	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 10:35:14.136385+00	\N
1237	\N	0013668	252713338	20260206	193442	전남87바1317	36.504026	127.429265	0	2.7	2.7	0	NOUSE	\N	36.504026	127.429265	2026-02-06 10:35:14.136385+00	\N
1238	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:35:14.136385+00	\N
1239	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:35:14.136385+00	\N
1240	\N	0013668	249253808	20260206	193242	전남87바1325	36.808644	127.497856	1	18.9	-18.9	0	NOUSE	\N	36.808644	127.497856	2026-02-06 10:35:14.136385+00	\N
1241	\N	0013668	252214998	20260206	193037	전남87바1326	35.378304	129.025776	1	19.2	-19.2	0	2.7	2.7	35.378304	129.025776	2026-02-06 10:35:14.136385+00	\N
1242	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:35:14.136385+00	\N
1243	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:35:14.136385+00	\N
1244	\N	0013668	251512431	20260206	190910	전남87바1351	37.248838	127.423753	1	25.1	-25.1	0	NOUSE	\N	37.248838	127.423753	2026-02-06 10:35:14.136385+00	\N
1245	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:35:14.136385+00	\N
1246	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:35:14.136385+00	\N
1247	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:35:14.136385+00	\N
1248	\N	0013668	236994200	20260206	193508	전남87바1362	36.198703	127.263804	0	1.6	1.6	0	2.8	2.8	36.198703	127.263804	2026-02-06 10:35:14.136385+00	\N
1249	\N	0013668	252215001	20260206	191540	전남87바1364	37.087188	127.216976	0	3.7	3.7	0	NOUSE	\N	37.087188	127.216976	2026-02-06 10:35:14.136385+00	\N
1250	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:35:14.136385+00	\N
1251	\N	0013668	251512435	20260206	193413	전남87바1368	35.258326	128.825275	1	18.6	-18.6	0	3.8	3.8	35.258326	128.825275	2026-02-06 10:35:14.136385+00	\N
1252	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:35:14.136385+00	\N
1253	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:35:14.136385+00	\N
1254	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:35:14.136385+00	\N
1255	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:35:14.136385+00	\N
1256	\N	0013668	235994979	20260206	193404	전남87바4157	35.671568	126.733696	0	5.2	5.2	0	NOUSE	\N	35.671568	126.733696	2026-02-06 10:35:14.136385+00	\N
1257	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:35:14.136385+00	\N
1258	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:35:14.136385+00	\N
1259	\N	0013668	252799355	20260206	193442	전남87바4161	35.831236	128.699720	1	22.9	-22.9	0	NOUSE	\N	35.831236	128.69972	2026-02-06 10:35:14.136385+00	\N
1260	\N	0013668	252227303	20260206	193222	전남87바4162	35.216224	126.490504	0	2.3	2.3	0	NOUSE	\N	35.216224	126.490504	2026-02-06 10:35:14.136385+00	\N
1261	\N	0013668	251512429	20260206	191528	전남87바4165	37.147991	127.384745	1	21.8	-21.8	0	NOUSE	\N	37.147991	127.384745	2026-02-06 10:35:14.136385+00	\N
1262	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:35:14.136385+00	\N
1263	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:35:14.136385+00	\N
1264	\N	0013668	251509223	20260206	193014	전남87바4173	36.290260	128.229825	1	20.8	-20.8	0	NOUSE	\N	36.29026	128.229825	2026-02-06 10:35:14.136385+00	\N
1265	\N	0013668	252228112	20260206	192012	전남87바4174	35.320380	126.754328	1	21.1	-21.1	0	NOUSE	\N	35.32038	126.754328	2026-02-06 10:35:14.136385+00	\N
1266	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:35:14.136385+00	\N
1267	\N	0013668	252214992	20260206	193012	전남87바4176	35.018476	127.358632	0	3.1	3.1	0	NOUSE	\N	35.018476	127.358632	2026-02-06 10:35:14.136385+00	\N
1268	\N	0013668	239200586	20260206	193344	전남87바4177	36.472043	128.201202	0	5.2	5.2	0	NOUSE	\N	36.472043	128.201202	2026-02-06 10:35:14.136385+00	\N
1269	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:35:14.136385+00	\N
1270	\N	0013668	240074478	20260206	193105	전남87바4188	35.736268	126.988528	1	21.5	-21.5	0	NOUSE	\N	35.736268	126.988528	2026-02-06 10:35:14.136385+00	\N
1271	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:35:14.136385+00	\N
1413	\N	0013668	252215001	20260206	191540	전남87바1364	37.087188	127.216976	0	3.7	3.7	0	NOUSE	\N	37.087188	127.216976	2026-02-06 10:52:02.949046+00	\N
1414	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:52:02.949046+00	\N
1415	\N	0013668	251512435	20260206	194914	전남87바1368	35.258302	128.825201	1	18.8	-18.8	0	5.0	5	35.258302	128.825201	2026-02-06 10:52:02.949046+00	\N
1416	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:52:02.949046+00	\N
1417	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:52:02.949046+00	\N
1418	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:52:02.949046+00	\N
1272	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:35:14.247368+00	\N
1273	\N	0013668	236275896	20260206	193326	전남87바1302	0.000000	0.000000	0	1.5	1.5	0	NOUSE	\N	0	0	2026-02-06 10:35:14.247368+00	\N
1274	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:35:14.247368+00	\N
1275	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:35:14.247368+00	\N
1276	\N	0013668	252227307	20260206	193245	전남87바1305	35.375648	129.046920	0	2.1	2.1	0	NOUSE	\N	35.375648	129.04692	2026-02-06 10:35:14.247368+00	\N
1277	\N	0013668	252214997	20260206	155916	전남87바1313	37.087444	127.217376	1	19.8	-19.8	0	NOUSE	\N	37.087444	127.217376	2026-02-06 10:35:14.247368+00	\N
1278	\N	0013668	252713338	20260206	193442	전남87바1317	36.504026	127.429265	0	2.7	2.7	0	NOUSE	\N	36.504026	127.429265	2026-02-06 10:35:14.247368+00	\N
1279	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:35:14.247368+00	\N
1280	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:35:14.247368+00	\N
1281	\N	0013668	249253808	20260206	193242	전남87바1325	36.808644	127.497856	1	18.9	-18.9	0	NOUSE	\N	36.808644	127.497856	2026-02-06 10:35:14.247368+00	\N
1282	\N	0013668	252214998	20260206	193037	전남87바1326	35.378304	129.025776	1	19.2	-19.2	0	2.7	2.7	35.378304	129.025776	2026-02-06 10:35:14.247368+00	\N
1283	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:35:14.247368+00	\N
1284	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:35:14.247368+00	\N
1285	\N	0013668	251512431	20260206	190910	전남87바1351	37.248838	127.423753	1	25.1	-25.1	0	NOUSE	\N	37.248838	127.423753	2026-02-06 10:35:14.247368+00	\N
1286	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:35:14.247368+00	\N
1287	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:35:14.247368+00	\N
1288	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:35:14.247368+00	\N
1289	\N	0013668	236994200	20260206	193508	전남87바1362	36.198703	127.263804	0	1.6	1.6	0	2.8	2.8	36.198703	127.263804	2026-02-06 10:35:14.247368+00	\N
1290	\N	0013668	252215001	20260206	191540	전남87바1364	37.087188	127.216976	0	3.7	3.7	0	NOUSE	\N	37.087188	127.216976	2026-02-06 10:35:14.247368+00	\N
1291	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:35:14.247368+00	\N
1292	\N	0013668	251512435	20260206	193413	전남87바1368	35.258326	128.825275	1	18.6	-18.6	0	3.8	3.8	35.258326	128.825275	2026-02-06 10:35:14.247368+00	\N
1293	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:35:14.247368+00	\N
1294	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:35:14.247368+00	\N
1295	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:35:14.247368+00	\N
1296	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:35:14.247368+00	\N
1297	\N	0013668	235994979	20260206	193404	전남87바4157	35.671568	126.733696	0	5.2	5.2	0	NOUSE	\N	35.671568	126.733696	2026-02-06 10:35:14.247368+00	\N
1298	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:35:14.247368+00	\N
1299	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:35:14.247368+00	\N
1300	\N	0013668	252799355	20260206	193442	전남87바4161	35.831236	128.699720	1	22.9	-22.9	0	NOUSE	\N	35.831236	128.69972	2026-02-06 10:35:14.247368+00	\N
1301	\N	0013668	252227303	20260206	193222	전남87바4162	35.216224	126.490504	0	2.3	2.3	0	NOUSE	\N	35.216224	126.490504	2026-02-06 10:35:14.247368+00	\N
1302	\N	0013668	251512429	20260206	191528	전남87바4165	37.147991	127.384745	1	21.8	-21.8	0	NOUSE	\N	37.147991	127.384745	2026-02-06 10:35:14.247368+00	\N
1303	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:35:14.247368+00	\N
1304	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:35:14.247368+00	\N
1305	\N	0013668	251509223	20260206	193014	전남87바4173	36.290260	128.229825	1	20.8	-20.8	0	NOUSE	\N	36.29026	128.229825	2026-02-06 10:35:14.247368+00	\N
1306	\N	0013668	252228112	20260206	192012	전남87바4174	35.320380	126.754328	1	21.1	-21.1	0	NOUSE	\N	35.32038	126.754328	2026-02-06 10:35:14.247368+00	\N
1307	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:35:14.247368+00	\N
1308	\N	0013668	252214992	20260206	193012	전남87바4176	35.018476	127.358632	0	3.1	3.1	0	NOUSE	\N	35.018476	127.358632	2026-02-06 10:35:14.247368+00	\N
1309	\N	0013668	239200586	20260206	193344	전남87바4177	36.472043	128.201202	0	5.2	5.2	0	NOUSE	\N	36.472043	128.201202	2026-02-06 10:35:14.247368+00	\N
1310	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:35:14.247368+00	\N
1311	\N	0013668	240074478	20260206	193105	전남87바4188	35.736268	126.988528	1	21.5	-21.5	0	NOUSE	\N	35.736268	126.988528	2026-02-06 10:35:14.247368+00	\N
1312	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:35:14.247368+00	\N
1419	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:52:02.949046+00	\N
1420	\N	0013668	235994979	20260206	194904	전남87바4157	35.671572	126.733704	0	5.2	5.2	0	NOUSE	\N	35.671572	126.733704	2026-02-06 10:52:02.949046+00	\N
1421	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:52:02.949046+00	\N
1422	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:52:02.949046+00	\N
1423	\N	0013668	252799355	20260206	194942	전남87바4161	35.656756	128.745792	1	19.6	-19.6	0	NOUSE	\N	35.656756	128.745792	2026-02-06 10:52:02.949046+00	\N
1424	\N	0013668	252227303	20260206	194722	전남87바4162	35.384144	126.612832	0	2.7	2.7	0	NOUSE	\N	35.384144	126.612832	2026-02-06 10:52:02.949046+00	\N
1425	\N	0013668	251512429	20260206	191528	전남87바4165	37.147991	127.384745	1	21.8	-21.8	0	NOUSE	\N	37.147991	127.384745	2026-02-06 10:52:02.949046+00	\N
1426	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:52:02.949046+00	\N
1427	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:52:02.949046+00	\N
1428	\N	0013668	251509223	20260206	195021	전남87바4173	36.107702	128.361054	1	19.7	-19.7	0	NOUSE	\N	36.107702	128.361054	2026-02-06 10:52:02.949046+00	\N
1429	\N	0013668	252228112	20260206	192012	전남87바4174	35.320380	126.754328	1	21.1	-21.1	0	NOUSE	\N	35.32038	126.754328	2026-02-06 10:52:02.949046+00	\N
1430	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:52:02.949046+00	\N
1431	\N	0013668	252214992	20260206	195012	전남87바4176	35.210612	127.235072	0	2.6	2.6	0	NOUSE	\N	35.210612	127.235072	2026-02-06 10:52:02.949046+00	\N
1432	\N	0013668	239200586	20260206	194850	전남87바4177	36.619811	128.152410	0	5.8	5.8	0	NOUSE	\N	36.619811	128.15241	2026-02-06 10:52:02.949046+00	\N
1433	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:52:02.949046+00	\N
1434	\N	0013668	240074478	20260206	195105	전남87바4188	35.536488	126.813224	1	23.3	-23.3	0	NOUSE	\N	35.536488	126.813224	2026-02-06 10:52:02.949046+00	\N
1435	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:52:02.949046+00	\N
1436	\N	0013668	239209332	20251129	160912	광주85사1706	36.973408	127.247848	0	3.2	3.2	0	NOUSE	\N	36.973408	127.247848	2026-02-06 10:52:02.956284+00	\N
1437	\N	0013668	236275896	20260206	194826	전남87바1302	35.168472	126.781480	0	1.3	1.3	0	NOUSE	\N	35.168472	126.78148	2026-02-06 10:52:02.956284+00	\N
1438	\N	0013668	252215336	20260103	112103	전남87바1303	36.932868	127.234824	0	OPEN	\N	0	NOUSE	\N	36.932868	127.234824	2026-02-06 10:52:02.956284+00	\N
1439	\N	0013668	251512430	20260204	021432	전남87바1304	35.247967	127.038917	0	0.2	0.2	0	NOUSE	\N	35.247967	127.038917	2026-02-06 10:52:02.956284+00	\N
1440	\N	0013668	252227307	20260206	194745	전남87바1305	35.530112	129.107760	0	2.8	2.8	0	NOUSE	\N	35.530112	129.10776	2026-02-06 10:52:02.956284+00	\N
1441	\N	0013668	252214997	20260206	194916	전남87바1313	37.266500	127.499336	1	18.6	-18.6	0	NOUSE	\N	37.2665	127.499336	2026-02-06 10:52:02.956284+00	\N
1442	\N	0013668	252713338	20260206	194948	전남87바1317	36.687862	127.425547	0	2.7	2.7	0	NOUSE	\N	36.687862	127.425547	2026-02-06 10:52:02.956284+00	\N
1443	\N	0013668	252227646	20260203	120843	전남87바1318	35.196588	126.791544	0	4.7	4.7	0	NOUSE	\N	35.196588	126.791544	2026-02-06 10:52:02.956284+00	\N
1444	\N	0013668	252214999	20260206	152357	전남87바1320	37.277480	127.523352	1	22.2	-22.2	0	NOUSE	\N	37.27748	127.523352	2026-02-06 10:52:02.956284+00	\N
1445	\N	0013668	249253808	20260206	194742	전남87바1325	36.984048	127.471768	1	20.4	-20.4	0	NOUSE	\N	36.984048	127.471768	2026-02-06 10:52:02.956284+00	\N
1446	\N	0013668	252214998	20260206	195037	전남87바1326	35.273656	128.973832	1	19.8	-19.8	1	1.3	-1.3	35.273656	128.973832	2026-02-06 10:52:02.956284+00	\N
1447	\N	0013668	252227300	20250725	014442	전남87바1328	35.248020	127.039448	1	0.7	-0.7	0	NOUSE	\N	35.24802	127.039448	2026-02-06 10:52:02.956284+00	\N
1448	\N	0013668	252228119	20260206	175524	전남87바1336	37.087180	127.217088	0	4.5	4.5	0	NOUSE	\N	37.08718	127.217088	2026-02-06 10:52:02.956284+00	\N
1449	\N	0013668	251512431	20260206	190910	전남87바1351	37.248838	127.423753	1	25.1	-25.1	0	NOUSE	\N	37.248838	127.423753	2026-02-06 10:52:02.956284+00	\N
1450	\N	0013668	252227306	20260203	153418	전남87바1352	37.147356	127.383328	0	4.9	4.9	0	NOUSE	\N	37.147356	127.383328	2026-02-06 10:52:02.956284+00	\N
1451	\N	0013668	252214996	20260205	101046	전남87바1356	37.145064	127.394640	1	14.1	-14.1	0	NOUSE	\N	37.145064	127.39464	2026-02-06 10:52:02.956284+00	\N
1452	\N	0013668	252227305	20260206	134311	전남87바1361	35.248012	127.040256	1	19.1	-19.1	0	NOUSE	\N	35.248012	127.040256	2026-02-06 10:52:02.956284+00	\N
1453	\N	0013668	236994200	20260206	195013	전남87바1362	36.085836	127.104505	0	1.8	1.8	0	2.9	2.9	36.085836	127.104505	2026-02-06 10:52:02.956284+00	\N
1454	\N	0013668	252215001	20260206	191540	전남87바1364	37.087188	127.216976	0	3.7	3.7	0	NOUSE	\N	37.087188	127.216976	2026-02-06 10:52:02.956284+00	\N
1455	\N	0013668	235771010	20260206	163431	전남87바1367	35.834343	126.808985	0	0.2	0.2	0	NOUSE	\N	35.834343	126.808985	2026-02-06 10:52:02.956284+00	\N
1456	\N	0013668	251512435	20260206	194914	전남87바1368	35.258302	128.825201	1	18.8	-18.8	0	5.0	5	35.258302	128.825201	2026-02-06 10:52:02.956284+00	\N
1457	\N	0013668	252227308	20260101	143707	전남87바1371	0.000000	0.000000	0	OPEN	\N	0	NOUSE	\N	0	0	2026-02-06 10:52:02.956284+00	\N
1458	\N	0013668	252227304	20260206	180612	전남87바1373	35.244916	127.024504	1	17.0	-17	0	NOUSE	\N	35.244916	127.024504	2026-02-06 10:52:02.956284+00	\N
1459	\N	0013668	252227301	20260131	202937	전남87바4155	35.197764	126.846136	0	3.2	3.2	0	NOUSE	\N	35.197764	126.846136	2026-02-06 10:52:02.956284+00	\N
1460	\N	0013668	235980831	20260206	184007	전남87바4156	35.125887	126.762048	0	3.9	3.9	0	NOUSE	\N	35.125887	126.762048	2026-02-06 10:52:02.956284+00	\N
1461	\N	0013668	235994979	20260206	194904	전남87바4157	35.671572	126.733704	0	5.2	5.2	0	NOUSE	\N	35.671572	126.733704	2026-02-06 10:52:02.956284+00	\N
1462	\N	0013668	235771783	20260206	094659	전남87바4158	37.147318	127.383889	0	3.2	3.2	0	NOUSE	\N	37.147318	127.383889	2026-02-06 10:52:02.956284+00	\N
1463	\N	0013668	252215000	20260206	135324	전남87바4159	37.147504	127.384120	1	18.9	-18.9	0	NOUSE	\N	37.147504	127.38412	2026-02-06 10:52:02.956284+00	\N
1464	\N	0013668	252799355	20260206	194942	전남87바4161	35.656756	128.745792	1	19.6	-19.6	0	NOUSE	\N	35.656756	128.745792	2026-02-06 10:52:02.956284+00	\N
1465	\N	0013668	252227303	20260206	194722	전남87바4162	35.384144	126.612832	0	2.7	2.7	0	NOUSE	\N	35.384144	126.612832	2026-02-06 10:52:02.956284+00	\N
1466	\N	0013668	251512429	20260206	191528	전남87바4165	37.147991	127.384745	1	21.8	-21.8	0	NOUSE	\N	37.147991	127.384745	2026-02-06 10:52:02.956284+00	\N
1467	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:52:02.956284+00	\N
1468	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:52:02.956284+00	\N
1469	\N	0013668	251509223	20260206	195021	전남87바4173	36.107702	128.361054	1	19.7	-19.7	0	NOUSE	\N	36.107702	128.361054	2026-02-06 10:52:02.956284+00	\N
1470	\N	0013668	252228112	20260206	192012	전남87바4174	35.320380	126.754328	1	21.1	-21.1	0	NOUSE	\N	35.32038	126.754328	2026-02-06 10:52:02.956284+00	\N
1471	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:52:02.956284+00	\N
1472	\N	0013668	252214992	20260206	195012	전남87바4176	35.210612	127.235072	0	2.6	2.6	0	NOUSE	\N	35.210612	127.235072	2026-02-06 10:52:02.956284+00	\N
1473	\N	0013668	239200586	20260206	194850	전남87바4177	36.619811	128.152410	0	5.8	5.8	0	NOUSE	\N	36.619811	128.15241	2026-02-06 10:52:02.956284+00	\N
1474	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:52:02.956284+00	\N
1475	\N	0013668	240074478	20260206	195105	전남87바4188	35.536488	126.813224	1	23.3	-23.3	0	NOUSE	\N	35.536488	126.813224	2026-02-06 10:52:02.956284+00	\N
1476	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:52:02.956284+00	\N
1045	\N	0013668	252799355	20260206	192442	전남87바4161	35.916784	128.634488	1	21.5	-21.5	0	NOUSE	\N	35.916784	128.634488	2026-02-06 10:25:14.139636+00	\N
1055	\N	0013668	252227303	20260206	192222	전남87바4162	35.085436	126.480784	0	2.2	2.2	0	NOUSE	\N	35.085436	126.480784	2026-02-06 10:25:14.139636+00	\N
1056	\N	0013668	251512429	20260206	191528	전남87바4165	37.147991	127.384745	1	21.8	-21.8	0	NOUSE	\N	37.147991	127.384745	2026-02-06 10:25:14.139636+00	\N
1057	\N	0013668	236272742	20260206	172028	전남87바4166	37.248944	127.423536	1	16.9	-16.9	1	10.9	-10.9	37.248944	127.423536	2026-02-06 10:25:14.139636+00	\N
1058	\N	0013668	252214993	20260206	131058	전남87바4169	37.087164	127.216952	0	1.3	1.3	0	NOUSE	\N	37.087164	127.216952	2026-02-06 10:25:14.139636+00	\N
1059	\N	0013668	251509223	20260206	192512	전남87바4173	36.340141	128.223310	1	19.8	-19.8	0	NOUSE	\N	36.340141	128.22331	2026-02-06 10:25:14.139636+00	\N
1060	\N	0013668	252228112	20260206	192012	전남87바4174	35.320380	126.754328	1	21.1	-21.1	0	NOUSE	\N	35.32038	126.754328	2026-02-06 10:25:14.139636+00	\N
1061	\N	0013668	252227302	20250825	074436	전남87바4175	35.644888	126.921248	1	1.4	-1.4	0	NOUSE	\N	35.644888	126.921248	2026-02-06 10:25:14.139636+00	\N
1062	\N	0013668	252214992	20260206	192012	전남87바4176	35.003140	127.484792	0	2.5	2.5	0	NOUSE	\N	35.00314	127.484792	2026-02-06 10:25:14.139636+00	\N
1063	\N	0013668	239200586	20260206	192341	전남87바4177	36.372121	128.257286	0	3.7	3.7	0	NOUSE	\N	36.372121	128.257286	2026-02-06 10:25:14.139636+00	\N
1064	\N	0013668	252212696	20260128	095718	전남87바4179	36.901609	127.017295	1	21.3	-21.3	0	NOUSE	\N	36.901609	127.017295	2026-02-06 10:25:14.139636+00	\N
1065	\N	0013668	240074478	20260206	192105	전남87바4188	35.849112	127.048568	1	22.3	-22.3	0	NOUSE	\N	35.849112	127.048568	2026-02-06 10:25:14.139636+00	\N
1066	\N	0013668	235777403	20250415	152656	전남87바4401	0.000000	0.000000	0	4.7	4.7	0	NOUSE	\N	0	0	2026-02-06 10:25:14.139636+00	\N
\.


--
-- Name: ai_chat_histories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.ai_chat_histories_id_seq', 1, false);


--
-- Name: ai_usage_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.ai_usage_logs_id_seq', 1, false);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 1, false);


--
-- Name: band_chat_rooms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.band_chat_rooms_id_seq', 1, false);


--
-- Name: band_message_schedules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.band_message_schedules_id_seq', 1, false);


--
-- Name: band_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.band_messages_id_seq', 1, false);


--
-- Name: billing_policies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.billing_policies_id_seq', 1, false);


--
-- Name: clients_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.clients_id_seq', 1, false);


--
-- Name: dispatch_routes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.dispatch_routes_id_seq', 1, false);


--
-- Name: dispatches_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.dispatches_id_seq', 1, false);


--
-- Name: driver_schedules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.driver_schedules_id_seq', 1, false);


--
-- Name: driver_settlement_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.driver_settlement_items_id_seq', 1, false);


--
-- Name: driver_settlements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.driver_settlements_id_seq', 1, false);


--
-- Name: drivers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.drivers_id_seq', 1, false);


--
-- Name: fcm_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.fcm_tokens_id_seq', 1, false);


--
-- Name: invoice_line_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.invoice_line_items_id_seq', 1, false);


--
-- Name: invoices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.invoices_id_seq', 1, false);


--
-- Name: maintenance_part_usage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.maintenance_part_usage_id_seq', 1, false);


--
-- Name: maintenance_schedules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.maintenance_schedules_id_seq', 1, false);


--
-- Name: notices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.notices_id_seq', 1, false);


--
-- Name: notification_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.notification_templates_id_seq', 1, false);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.notifications_id_seq', 1, false);


--
-- Name: order_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.order_templates_id_seq', 1, false);


--
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.orders_id_seq', 1, false);


--
-- Name: payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.payments_id_seq', 1, false);


--
-- Name: purchase_orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.purchase_orders_id_seq', 1, false);


--
-- Name: push_notification_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.push_notification_logs_id_seq', 1, false);


--
-- Name: recurring_orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.recurring_orders_id_seq', 1, false);


--
-- Name: security_alerts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.security_alerts_id_seq', 1, false);


--
-- Name: temperature_alerts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.temperature_alerts_id_seq', 1, false);


--
-- Name: two_factor_auth_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.two_factor_auth_id_seq', 1, false);


--
-- Name: two_factor_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.two_factor_logs_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: uvis_access_keys_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.uvis_access_keys_id_seq', 30, true);


--
-- Name: uvis_api_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.uvis_api_logs_id_seq', 68, true);


--
-- Name: vehicle_gps_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.vehicle_gps_logs_id_seq', 1, false);


--
-- Name: vehicle_inspections_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.vehicle_inspections_id_seq', 1, false);


--
-- Name: vehicle_locations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.vehicle_locations_id_seq', 1, false);


--
-- Name: vehicle_maintenance_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.vehicle_maintenance_records_id_seq', 1, false);


--
-- Name: vehicle_parts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.vehicle_parts_id_seq', 1, false);


--
-- Name: vehicle_temperature_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.vehicle_temperature_logs_id_seq', 1476, true);


--
-- Name: vehicles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: uvis_user
--

SELECT pg_catalog.setval('public.vehicles_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--

\unrestrict fHS72CWYc590y619DIAduvPv1t0If43Fd8dNaVrwe3FXgGazTnEHHZek25uN2g7

