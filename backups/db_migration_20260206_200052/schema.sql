--
-- PostgreSQL database dump
--

\restrict 6NL0AqDvjEWX3nPVmLNQ61iDEeHywD56zJrevsoDR76NgZh4gJpbI7qnbK4bzBz

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
-- Name: billingcycletype; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.billingcycletype AS ENUM (
    'IMMEDIATE',
    'WEEKLY',
    'MONTHLY',
    'CUSTOM'
);


ALTER TYPE public.billingcycletype OWNER TO uvis_user;

--
-- Name: billingstatus; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.billingstatus AS ENUM (
    'DRAFT',
    'PENDING',
    'SENT',
    'PARTIAL',
    'PAID',
    'OVERDUE',
    'CANCELLED'
);


ALTER TYPE public.billingstatus OWNER TO uvis_user;

--
-- Name: clienttype; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.clienttype AS ENUM (
    'PICKUP',
    'DELIVERY',
    'BOTH'
);


ALTER TYPE public.clienttype OWNER TO uvis_user;

--
-- Name: dispatchstatus; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.dispatchstatus AS ENUM (
    'DRAFT',
    'CONFIRMED',
    'IN_PROGRESS',
    'COMPLETED',
    'CANCELLED'
);


ALTER TYPE public.dispatchstatus OWNER TO uvis_user;

--
-- Name: maintenancepriority; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.maintenancepriority AS ENUM (
    'LOW',
    'MEDIUM',
    'HIGH',
    'URGENT'
);


ALTER TYPE public.maintenancepriority OWNER TO uvis_user;

--
-- Name: maintenancestatus; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.maintenancestatus AS ENUM (
    'SCHEDULED',
    'IN_PROGRESS',
    'COMPLETED',
    'CANCELLED'
);


ALTER TYPE public.maintenancestatus OWNER TO uvis_user;

--
-- Name: maintenancetype; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.maintenancetype AS ENUM (
    'REGULAR',
    'REPAIR',
    'PARTS_REPLACEMENT',
    'OIL_CHANGE',
    'TIRE_CHANGE',
    'BRAKE',
    'BATTERY',
    'ACCIDENT_REPAIR',
    'EMERGENCY',
    'OTHER'
);


ALTER TYPE public.maintenancetype OWNER TO uvis_user;

--
-- Name: notificationchannel; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.notificationchannel AS ENUM (
    'SMS',
    'KAKAO',
    'PUSH',
    'EMAIL'
);


ALTER TYPE public.notificationchannel OWNER TO uvis_user;

--
-- Name: notificationstatus; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.notificationstatus AS ENUM (
    'PENDING',
    'SENT',
    'FAILED',
    'DELIVERED',
    'READ'
);


ALTER TYPE public.notificationstatus OWNER TO uvis_user;

--
-- Name: notificationtype; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.notificationtype AS ENUM (
    'ORDER_CONFIRMED',
    'ORDER_CANCELLED',
    'DISPATCH_ASSIGNED',
    'DISPATCH_COMPLETED',
    'URGENT_DISPATCH',
    'TEMPERATURE_ALERT',
    'VEHICLE_MAINTENANCE',
    'DRIVER_SCHEDULE'
);


ALTER TYPE public.notificationtype OWNER TO uvis_user;

--
-- Name: orderstatus; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.orderstatus AS ENUM (
    'PENDING',
    'ASSIGNED',
    'IN_TRANSIT',
    'DELIVERED',
    'CANCELLED'
);


ALTER TYPE public.orderstatus OWNER TO uvis_user;

--
-- Name: partcategory; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.partcategory AS ENUM (
    'ENGINE',
    'TRANSMISSION',
    'BRAKE',
    'TIRE',
    'BATTERY',
    'OIL',
    'FILTER',
    'COOLANT',
    'BELT',
    'SUSPENSION',
    'ELECTRICAL',
    'BODY',
    'INTERIOR',
    'OTHER'
);


ALTER TYPE public.partcategory OWNER TO uvis_user;

--
-- Name: paymentmethod; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.paymentmethod AS ENUM (
    'CASH',
    'TRANSFER',
    'CARD',
    'CHECK'
);


ALTER TYPE public.paymentmethod OWNER TO uvis_user;

--
-- Name: recurringfrequency; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.recurringfrequency AS ENUM (
    'DAILY',
    'WEEKLY',
    'MONTHLY',
    'CUSTOM'
);


ALTER TYPE public.recurringfrequency OWNER TO uvis_user;

--
-- Name: routetype; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.routetype AS ENUM (
    'GARAGE_START',
    'PICKUP',
    'DELIVERY',
    'GARAGE_END'
);


ALTER TYPE public.routetype OWNER TO uvis_user;

--
-- Name: scheduletype; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.scheduletype AS ENUM (
    'WORK',
    'DAY_OFF',
    'VACATION',
    'SICK_LEAVE',
    'TRAINING'
);


ALTER TYPE public.scheduletype OWNER TO uvis_user;

--
-- Name: temperaturezone; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.temperaturezone AS ENUM (
    'FROZEN',
    'REFRIGERATED',
    'AMBIENT'
);


ALTER TYPE public.temperaturezone OWNER TO uvis_user;

--
-- Name: userrole; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.userrole AS ENUM (
    'ADMIN',
    'DISPATCHER',
    'DRIVER',
    'VIEWER'
);


ALTER TYPE public.userrole OWNER TO uvis_user;

--
-- Name: vehiclestatus; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.vehiclestatus AS ENUM (
    'AVAILABLE',
    'IN_USE',
    'MAINTENANCE',
    'EMERGENCY_MAINTENANCE',
    'BREAKDOWN',
    'OUT_OF_SERVICE'
);


ALTER TYPE public.vehiclestatus OWNER TO uvis_user;

--
-- Name: vehicletype; Type: TYPE; Schema: public; Owner: uvis_user
--

CREATE TYPE public.vehicletype AS ENUM (
    'FROZEN',
    'REFRIGERATED',
    'DUAL',
    'AMBIENT'
);


ALTER TYPE public.vehicletype OWNER TO uvis_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ai_chat_histories; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.ai_chat_histories (
    id integer NOT NULL,
    user_id integer,
    session_id character varying(255),
    user_message text NOT NULL,
    assistant_message text NOT NULL,
    intent character varying(100),
    action character varying(100),
    parsed_order json,
    parsed_orders json,
    dispatch_recommendation json,
    created_at timestamp without time zone
);


ALTER TABLE public.ai_chat_histories OWNER TO uvis_user;

--
-- Name: ai_chat_histories_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.ai_chat_histories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_chat_histories_id_seq OWNER TO uvis_user;

--
-- Name: ai_chat_histories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.ai_chat_histories_id_seq OWNED BY public.ai_chat_histories.id;


--
-- Name: ai_usage_logs; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.ai_usage_logs (
    id integer NOT NULL,
    user_id integer,
    session_id character varying(255),
    model_name character varying(100) NOT NULL,
    provider character varying(50) NOT NULL,
    prompt_tokens integer NOT NULL,
    completion_tokens integer NOT NULL,
    total_tokens integer NOT NULL,
    prompt_cost double precision NOT NULL,
    completion_cost double precision NOT NULL,
    total_cost double precision NOT NULL,
    response_time_ms integer,
    status character varying(50) NOT NULL,
    error_message text,
    intent character varying(100),
    created_at timestamp without time zone
);


ALTER TABLE public.ai_usage_logs OWNER TO uvis_user;

--
-- Name: ai_usage_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.ai_usage_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ai_usage_logs_id_seq OWNER TO uvis_user;

--
-- Name: ai_usage_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.ai_usage_logs_id_seq OWNED BY public.ai_usage_logs.id;


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    user_id integer,
    action character varying(100) NOT NULL,
    resource_type character varying(50),
    resource_id integer,
    details character varying(1000),
    ip_address character varying(50),
    user_agent character varying(255),
    status character varying(20),
    created_at timestamp without time zone
);


ALTER TABLE public.audit_logs OWNER TO uvis_user;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.audit_logs_id_seq OWNER TO uvis_user;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: band_chat_rooms; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.band_chat_rooms (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    band_url character varying(500) NOT NULL,
    description text,
    is_active boolean,
    last_message_at timestamp with time zone,
    total_messages integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.band_chat_rooms OWNER TO uvis_user;

--
-- Name: COLUMN band_chat_rooms.name; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_chat_rooms.name IS '채팅방 이름';


--
-- Name: COLUMN band_chat_rooms.band_url; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_chat_rooms.band_url IS '밴드 URL';


--
-- Name: COLUMN band_chat_rooms.description; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_chat_rooms.description IS '설명';


--
-- Name: COLUMN band_chat_rooms.is_active; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_chat_rooms.is_active IS '활성화 여부';


--
-- Name: COLUMN band_chat_rooms.last_message_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_chat_rooms.last_message_at IS '마지막 메시지 전송 시간';


--
-- Name: COLUMN band_chat_rooms.total_messages; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_chat_rooms.total_messages IS '총 메시지 수';


--
-- Name: COLUMN band_chat_rooms.created_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_chat_rooms.created_at IS '생성일시';


--
-- Name: COLUMN band_chat_rooms.updated_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_chat_rooms.updated_at IS '수정일시';


--
-- Name: band_chat_rooms_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.band_chat_rooms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.band_chat_rooms_id_seq OWNER TO uvis_user;

--
-- Name: band_chat_rooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.band_chat_rooms_id_seq OWNED BY public.band_chat_rooms.id;


--
-- Name: band_message_schedules; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.band_message_schedules (
    id integer NOT NULL,
    dispatch_id integer NOT NULL,
    is_active boolean,
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone NOT NULL,
    min_interval_seconds integer,
    max_interval_seconds integer,
    messages_generated integer,
    last_generated_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.band_message_schedules OWNER TO uvis_user;

--
-- Name: COLUMN band_message_schedules.dispatch_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_message_schedules.dispatch_id IS '배차 ID';


--
-- Name: COLUMN band_message_schedules.is_active; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_message_schedules.is_active IS '스케줄 활성화';


--
-- Name: COLUMN band_message_schedules.start_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_message_schedules.start_time IS '시작 시간';


--
-- Name: COLUMN band_message_schedules.end_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_message_schedules.end_time IS '종료 시간';


--
-- Name: COLUMN band_message_schedules.min_interval_seconds; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_message_schedules.min_interval_seconds IS '최소 간격 (초)';


--
-- Name: COLUMN band_message_schedules.max_interval_seconds; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_message_schedules.max_interval_seconds IS '최대 간격 (초)';


--
-- Name: COLUMN band_message_schedules.messages_generated; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_message_schedules.messages_generated IS '생성된 메시지 수';


--
-- Name: COLUMN band_message_schedules.last_generated_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_message_schedules.last_generated_at IS '마지막 생성 시간';


--
-- Name: COLUMN band_message_schedules.created_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_message_schedules.created_at IS '생성일시';


--
-- Name: COLUMN band_message_schedules.updated_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_message_schedules.updated_at IS '수정일시';


--
-- Name: band_message_schedules_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.band_message_schedules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.band_message_schedules_id_seq OWNER TO uvis_user;

--
-- Name: band_message_schedules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.band_message_schedules_id_seq OWNED BY public.band_message_schedules.id;


--
-- Name: band_messages; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.band_messages (
    id integer NOT NULL,
    dispatch_id integer NOT NULL,
    message_content text NOT NULL,
    message_type character varying(50),
    is_sent boolean,
    sent_at timestamp with time zone,
    generated_at timestamp with time zone DEFAULT now(),
    scheduled_for timestamp with time zone,
    variation_seed integer
);


ALTER TABLE public.band_messages OWNER TO uvis_user;

--
-- Name: COLUMN band_messages.dispatch_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_messages.dispatch_id IS '배차 ID';


--
-- Name: COLUMN band_messages.message_content; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_messages.message_content IS '생성된 메시지 내용';


--
-- Name: COLUMN band_messages.message_type; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_messages.message_type IS '메시지 타입';


--
-- Name: COLUMN band_messages.is_sent; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_messages.is_sent IS '전송 여부 (수동 전송 확인)';


--
-- Name: COLUMN band_messages.sent_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_messages.sent_at IS '전송 일시';


--
-- Name: COLUMN band_messages.generated_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_messages.generated_at IS '생성 일시';


--
-- Name: COLUMN band_messages.scheduled_for; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_messages.scheduled_for IS '예약 전송 시간';


--
-- Name: COLUMN band_messages.variation_seed; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.band_messages.variation_seed IS '메시지 변형 시드';


--
-- Name: band_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.band_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.band_messages_id_seq OWNER TO uvis_user;

--
-- Name: band_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.band_messages_id_seq OWNED BY public.band_messages.id;


--
-- Name: billing_policies; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.billing_policies (
    id integer NOT NULL,
    client_id integer NOT NULL,
    billing_cycle public.billingcycletype,
    billing_day integer,
    payment_terms_days integer,
    base_rate_per_km double precision,
    base_rate_per_pallet double precision,
    base_rate_per_kg double precision,
    weekend_surcharge_rate double precision,
    night_surcharge_rate double precision,
    express_surcharge_rate double precision,
    temperature_control_rate double precision,
    volume_discount_threshold integer,
    volume_discount_rate double precision,
    is_active boolean,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.billing_policies OWNER TO uvis_user;

--
-- Name: billing_policies_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.billing_policies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.billing_policies_id_seq OWNER TO uvis_user;

--
-- Name: billing_policies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.billing_policies_id_seq OWNED BY public.billing_policies.id;


--
-- Name: clients; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.clients (
    code character varying(50) NOT NULL,
    name character varying(200) NOT NULL,
    client_type public.clienttype NOT NULL,
    address character varying(500) NOT NULL,
    address_detail character varying(200),
    latitude double precision,
    longitude double precision,
    geocoded boolean NOT NULL,
    geocode_error text,
    pickup_start_time character varying(5),
    pickup_end_time character varying(5),
    delivery_start_time character varying(5),
    delivery_end_time character varying(5),
    forklift_operator_available boolean NOT NULL,
    loading_time_minutes integer NOT NULL,
    contact_person character varying(100),
    phone character varying(20),
    notes text,
    is_active boolean NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.clients OWNER TO uvis_user;

--
-- Name: COLUMN clients.code; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.clients.code IS '거래처코드';


--
-- Name: COLUMN clients.name; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.clients.name IS '거래처명';


--
-- Name: COLUMN clients.client_type; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.clients.client_type IS '상차/하차 구분';


--
-- Name: COLUMN clients.address; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.clients.address IS '기본 주소';


--
-- Name: COLUMN clients.address_detail; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.clients.address_detail IS '상세 주소';


--
-- Name: COLUMN clients.latitude; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.clients.latitude IS '위도';


--
-- Name: COLUMN clients.longitude; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.clients.longitude IS '경도';


--
-- Name: COLUMN clients.geocoded; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.clients.geocoded IS '지오코딩 완료 여부';


--
-- Name: COLUMN clients.geocode_error; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.clients.geocode_error IS '지오코딩 오류 메시지';


--
-- Name: COLUMN clients.pickup_start_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.clients.pickup_start_time IS '상차가능시작시간(HH:MM)';


--
-- Name: COLUMN clients.pickup_end_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.clients.pickup_end_time IS '상차가능종료시간(HH:MM)';


--
-- Name: COLUMN clients.delivery_start_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.clients.delivery_start_time IS '하차가능시작시간(HH:MM)';


--
-- Name: COLUMN clients.delivery_end_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.clients.delivery_end_time IS '하차가능종료시간(HH:MM)';


--
-- Name: COLUMN clients.forklift_operator_available; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.clients.forklift_operator_available IS '지게차 운전능력 가능 여부';


--
-- Name: COLUMN clients.loading_time_minutes; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.clients.loading_time_minutes IS '평균 상하차 소요시간(분)';


--
-- Name: COLUMN clients.contact_person; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.clients.contact_person IS '담당자명';


--
-- Name: COLUMN clients.phone; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.clients.phone IS '전화번호';


--
-- Name: COLUMN clients.notes; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.clients.notes IS '특이사항';


--
-- Name: COLUMN clients.is_active; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.clients.is_active IS '사용 여부';


--
-- Name: clients_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.clients_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.clients_id_seq OWNER TO uvis_user;

--
-- Name: clients_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.clients_id_seq OWNED BY public.clients.id;


--
-- Name: dispatch_routes; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.dispatch_routes (
    dispatch_id integer NOT NULL,
    sequence integer NOT NULL,
    route_type public.routetype NOT NULL,
    order_id integer,
    location_name character varying(200) NOT NULL,
    address character varying(500) NOT NULL,
    latitude double precision NOT NULL,
    longitude double precision NOT NULL,
    distance_from_previous_km double precision,
    duration_from_previous_minutes integer,
    estimated_arrival_time character varying(5),
    estimated_work_duration_minutes integer,
    estimated_departure_time character varying(5),
    current_pallets integer NOT NULL,
    current_weight_kg double precision NOT NULL,
    notes text,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.dispatch_routes OWNER TO uvis_user;

--
-- Name: COLUMN dispatch_routes.dispatch_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatch_routes.dispatch_id IS '배차 ID';


--
-- Name: COLUMN dispatch_routes.sequence; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatch_routes.sequence IS '경로 순서';


--
-- Name: COLUMN dispatch_routes.route_type; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatch_routes.route_type IS '경로 유형';


--
-- Name: COLUMN dispatch_routes.order_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatch_routes.order_id IS '주문 ID';


--
-- Name: COLUMN dispatch_routes.location_name; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatch_routes.location_name IS '위치명';


--
-- Name: COLUMN dispatch_routes.address; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatch_routes.address IS '주소';


--
-- Name: COLUMN dispatch_routes.latitude; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatch_routes.latitude IS '위도';


--
-- Name: COLUMN dispatch_routes.longitude; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatch_routes.longitude IS '경도';


--
-- Name: COLUMN dispatch_routes.distance_from_previous_km; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatch_routes.distance_from_previous_km IS '이전 지점 거리(km)';


--
-- Name: COLUMN dispatch_routes.duration_from_previous_minutes; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatch_routes.duration_from_previous_minutes IS '이전 지점 소요시간(분)';


--
-- Name: COLUMN dispatch_routes.estimated_arrival_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatch_routes.estimated_arrival_time IS '예상 도착시간(HH:MM)';


--
-- Name: COLUMN dispatch_routes.estimated_work_duration_minutes; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatch_routes.estimated_work_duration_minutes IS '예상 작업시간(분)';


--
-- Name: COLUMN dispatch_routes.estimated_departure_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatch_routes.estimated_departure_time IS '예상 출발시간(HH:MM)';


--
-- Name: COLUMN dispatch_routes.current_pallets; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatch_routes.current_pallets IS '현재 적재 팔레트 수';


--
-- Name: COLUMN dispatch_routes.current_weight_kg; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatch_routes.current_weight_kg IS '현재 적재 중량(kg)';


--
-- Name: COLUMN dispatch_routes.notes; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatch_routes.notes IS '특이사항';


--
-- Name: dispatch_routes_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.dispatch_routes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dispatch_routes_id_seq OWNER TO uvis_user;

--
-- Name: dispatch_routes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.dispatch_routes_id_seq OWNED BY public.dispatch_routes.id;


--
-- Name: dispatches; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.dispatches (
    dispatch_number character varying(50) NOT NULL,
    dispatch_date date NOT NULL,
    vehicle_id integer NOT NULL,
    driver_id integer,
    total_orders integer NOT NULL,
    total_pallets integer NOT NULL,
    total_weight_kg double precision NOT NULL,
    total_distance_km double precision,
    empty_distance_km double precision,
    estimated_duration_minutes integer,
    estimated_cost double precision,
    status public.dispatchstatus NOT NULL,
    is_scheduled boolean NOT NULL,
    scheduled_for_date date,
    auto_confirm_at character varying(5),
    is_recurring boolean NOT NULL,
    recurring_pattern character varying(50),
    recurring_days character varying(100),
    is_urgent boolean NOT NULL,
    urgency_level integer,
    urgent_reason text,
    optimization_score double precision,
    ai_metadata json,
    notes text,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.dispatches OWNER TO uvis_user;

--
-- Name: COLUMN dispatches.dispatch_number; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.dispatch_number IS '배차번호';


--
-- Name: COLUMN dispatches.dispatch_date; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.dispatch_date IS '배차일자';


--
-- Name: COLUMN dispatches.vehicle_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.vehicle_id IS '차량 ID';


--
-- Name: COLUMN dispatches.driver_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.driver_id IS '기사 ID';


--
-- Name: COLUMN dispatches.total_orders; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.total_orders IS '총 주문 건수';


--
-- Name: COLUMN dispatches.total_pallets; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.total_pallets IS '총 팔레트 수';


--
-- Name: COLUMN dispatches.total_weight_kg; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.total_weight_kg IS '총 중량(kg)';


--
-- Name: COLUMN dispatches.total_distance_km; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.total_distance_km IS '총 주행거리(km)';


--
-- Name: COLUMN dispatches.empty_distance_km; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.empty_distance_km IS '공차거리(km)';


--
-- Name: COLUMN dispatches.estimated_duration_minutes; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.estimated_duration_minutes IS '예상 소요시간(분)';


--
-- Name: COLUMN dispatches.estimated_cost; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.estimated_cost IS '예상 비용';


--
-- Name: COLUMN dispatches.status; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.status IS '배차 상태';


--
-- Name: COLUMN dispatches.is_scheduled; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.is_scheduled IS '예약 배차 여부';


--
-- Name: COLUMN dispatches.scheduled_for_date; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.scheduled_for_date IS '예약된 배차일 (미래)';


--
-- Name: COLUMN dispatches.auto_confirm_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.auto_confirm_at IS '자동 확정 시간 (HH:MM)';


--
-- Name: COLUMN dispatches.is_recurring; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.is_recurring IS '정기 배차 여부';


--
-- Name: COLUMN dispatches.recurring_pattern; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.recurring_pattern IS '반복 패턴 (WEEKLY, MONTHLY)';


--
-- Name: COLUMN dispatches.recurring_days; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.recurring_days IS '반복 요일/날짜 (JSON)';


--
-- Name: COLUMN dispatches.is_urgent; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.is_urgent IS '긴급 배차 여부';


--
-- Name: COLUMN dispatches.urgency_level; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.urgency_level IS '긴급도 (1-5)';


--
-- Name: COLUMN dispatches.urgent_reason; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.urgent_reason IS '긴급 사유';


--
-- Name: COLUMN dispatches.optimization_score; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.optimization_score IS '최적화 점수';


--
-- Name: COLUMN dispatches.ai_metadata; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.ai_metadata IS 'AI 배차 메타데이터';


--
-- Name: COLUMN dispatches.notes; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.dispatches.notes IS '특이사항';


--
-- Name: dispatches_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.dispatches_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dispatches_id_seq OWNER TO uvis_user;

--
-- Name: dispatches_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.dispatches_id_seq OWNED BY public.dispatches.id;


--
-- Name: driver_schedules; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.driver_schedules (
    id integer NOT NULL,
    driver_id integer NOT NULL,
    schedule_date date NOT NULL,
    schedule_type public.scheduletype NOT NULL,
    start_time time without time zone,
    end_time time without time zone,
    is_available boolean,
    notes text,
    requires_approval boolean,
    is_approved boolean,
    approved_by integer,
    approval_notes text,
    created_at date DEFAULT now(),
    updated_at date
);


ALTER TABLE public.driver_schedules OWNER TO uvis_user;

--
-- Name: COLUMN driver_schedules.driver_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.driver_schedules.driver_id IS '기사 ID';


--
-- Name: COLUMN driver_schedules.schedule_date; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.driver_schedules.schedule_date IS '일정 날짜';


--
-- Name: COLUMN driver_schedules.schedule_type; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.driver_schedules.schedule_type IS '일정 유형';


--
-- Name: COLUMN driver_schedules.start_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.driver_schedules.start_time IS '근무 시작 시간';


--
-- Name: COLUMN driver_schedules.end_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.driver_schedules.end_time IS '근무 종료 시간';


--
-- Name: COLUMN driver_schedules.is_available; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.driver_schedules.is_available IS '배차 가능 여부';


--
-- Name: COLUMN driver_schedules.notes; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.driver_schedules.notes IS '비고';


--
-- Name: COLUMN driver_schedules.requires_approval; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.driver_schedules.requires_approval IS '승인 필요 여부';


--
-- Name: COLUMN driver_schedules.is_approved; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.driver_schedules.is_approved IS '승인 여부 (None: 대기, True: 승인, False: 거부)';


--
-- Name: COLUMN driver_schedules.approved_by; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.driver_schedules.approved_by IS '승인자 ID';


--
-- Name: COLUMN driver_schedules.approval_notes; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.driver_schedules.approval_notes IS '승인 메모';


--
-- Name: COLUMN driver_schedules.created_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.driver_schedules.created_at IS '생성 시간';


--
-- Name: COLUMN driver_schedules.updated_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.driver_schedules.updated_at IS '수정 시간';


--
-- Name: driver_schedules_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.driver_schedules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.driver_schedules_id_seq OWNER TO uvis_user;

--
-- Name: driver_schedules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.driver_schedules_id_seq OWNED BY public.driver_schedules.id;


--
-- Name: driver_settlement_items; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.driver_settlement_items (
    id integer NOT NULL,
    settlement_id integer NOT NULL,
    dispatch_id integer NOT NULL,
    revenue double precision NOT NULL,
    commission_rate double precision,
    commission_amount double precision,
    distance_km double precision,
    pallets integer,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.driver_settlement_items OWNER TO uvis_user;

--
-- Name: driver_settlement_items_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.driver_settlement_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.driver_settlement_items_id_seq OWNER TO uvis_user;

--
-- Name: driver_settlement_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.driver_settlement_items_id_seq OWNED BY public.driver_settlement_items.id;


--
-- Name: driver_settlements; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.driver_settlements (
    id integer NOT NULL,
    settlement_number character varying(50) NOT NULL,
    driver_id integer NOT NULL,
    settlement_period_start date NOT NULL,
    settlement_period_end date NOT NULL,
    total_revenue double precision,
    commission_amount double precision,
    expense_amount double precision,
    net_amount double precision,
    is_paid boolean,
    paid_date date,
    dispatch_count integer,
    total_distance_km double precision,
    total_pallets integer,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.driver_settlements OWNER TO uvis_user;

--
-- Name: driver_settlements_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.driver_settlements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.driver_settlements_id_seq OWNER TO uvis_user;

--
-- Name: driver_settlements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.driver_settlements_id_seq OWNED BY public.driver_settlements.id;


--
-- Name: drivers; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.drivers (
    code character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    phone character varying(20) NOT NULL,
    emergency_contact character varying(20),
    work_start_time character varying(5) NOT NULL,
    work_end_time character varying(5) NOT NULL,
    max_work_hours integer NOT NULL,
    license_number character varying(50),
    license_type character varying(20),
    notes text,
    is_active boolean NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.drivers OWNER TO uvis_user;

--
-- Name: COLUMN drivers.code; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.drivers.code IS '기사코드';


--
-- Name: COLUMN drivers.name; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.drivers.name IS '기사명';


--
-- Name: COLUMN drivers.phone; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.drivers.phone IS '전화번호';


--
-- Name: COLUMN drivers.emergency_contact; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.drivers.emergency_contact IS '비상연락처';


--
-- Name: COLUMN drivers.work_start_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.drivers.work_start_time IS '근무시작시간(HH:MM)';


--
-- Name: COLUMN drivers.work_end_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.drivers.work_end_time IS '근무종료시간(HH:MM)';


--
-- Name: COLUMN drivers.max_work_hours; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.drivers.max_work_hours IS '최대 근무시간';


--
-- Name: COLUMN drivers.license_number; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.drivers.license_number IS '운전면허번호';


--
-- Name: COLUMN drivers.license_type; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.drivers.license_type IS '면허 종류';


--
-- Name: COLUMN drivers.notes; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.drivers.notes IS '특이사항';


--
-- Name: COLUMN drivers.is_active; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.drivers.is_active IS '사용 여부';


--
-- Name: drivers_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.drivers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.drivers_id_seq OWNER TO uvis_user;

--
-- Name: drivers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.drivers_id_seq OWNED BY public.drivers.id;


--
-- Name: fcm_tokens; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.fcm_tokens (
    id integer NOT NULL,
    user_id integer NOT NULL,
    token character varying(255) NOT NULL,
    device_type character varying(20),
    device_id character varying(255),
    app_version character varying(20),
    is_active boolean,
    last_used_at timestamp without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.fcm_tokens OWNER TO uvis_user;

--
-- Name: fcm_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.fcm_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fcm_tokens_id_seq OWNER TO uvis_user;

--
-- Name: fcm_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.fcm_tokens_id_seq OWNED BY public.fcm_tokens.id;


--
-- Name: invoice_line_items; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.invoice_line_items (
    id integer NOT NULL,
    invoice_id integer NOT NULL,
    dispatch_id integer,
    description character varying(500) NOT NULL,
    quantity double precision,
    unit_price double precision NOT NULL,
    amount double precision NOT NULL,
    distance_km double precision,
    pallets integer,
    weight_kg double precision,
    surcharge_amount double precision,
    discount_amount double precision,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.invoice_line_items OWNER TO uvis_user;

--
-- Name: invoice_line_items_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.invoice_line_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.invoice_line_items_id_seq OWNER TO uvis_user;

--
-- Name: invoice_line_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.invoice_line_items_id_seq OWNED BY public.invoice_line_items.id;


--
-- Name: invoices; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.invoices (
    id integer NOT NULL,
    invoice_number character varying(50) NOT NULL,
    client_id integer NOT NULL,
    billing_period_start date NOT NULL,
    billing_period_end date NOT NULL,
    subtotal double precision,
    tax_amount double precision,
    discount_amount double precision,
    total_amount double precision,
    paid_amount double precision,
    status public.billingstatus,
    issue_date date NOT NULL,
    due_date date NOT NULL,
    paid_date date,
    notes text,
    pdf_url character varying(500),
    sent_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    created_by integer
);


ALTER TABLE public.invoices OWNER TO uvis_user;

--
-- Name: invoices_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.invoices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.invoices_id_seq OWNER TO uvis_user;

--
-- Name: invoices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.invoices_id_seq OWNED BY public.invoices.id;


--
-- Name: maintenance_part_usage; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.maintenance_part_usage (
    maintenance_record_id integer NOT NULL,
    part_id integer NOT NULL,
    quantity_used integer NOT NULL,
    unit_price double precision NOT NULL,
    total_price double precision NOT NULL,
    notes text,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.maintenance_part_usage OWNER TO uvis_user;

--
-- Name: COLUMN maintenance_part_usage.maintenance_record_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.maintenance_part_usage.maintenance_record_id IS '정비 기록 ID';


--
-- Name: COLUMN maintenance_part_usage.part_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.maintenance_part_usage.part_id IS '부품 ID';


--
-- Name: COLUMN maintenance_part_usage.quantity_used; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.maintenance_part_usage.quantity_used IS '사용 수량';


--
-- Name: COLUMN maintenance_part_usage.unit_price; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.maintenance_part_usage.unit_price IS '단가';


--
-- Name: COLUMN maintenance_part_usage.total_price; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.maintenance_part_usage.total_price IS '총액';


--
-- Name: COLUMN maintenance_part_usage.notes; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.maintenance_part_usage.notes IS '비고';


--
-- Name: maintenance_part_usage_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.maintenance_part_usage_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.maintenance_part_usage_id_seq OWNER TO uvis_user;

--
-- Name: maintenance_part_usage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.maintenance_part_usage_id_seq OWNED BY public.maintenance_part_usage.id;


--
-- Name: maintenance_schedules; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.maintenance_schedules (
    vehicle_id integer NOT NULL,
    maintenance_type public.maintenancetype NOT NULL,
    interval_km double precision,
    interval_months integer,
    last_maintenance_date date,
    last_maintenance_odometer double precision,
    next_maintenance_date date,
    next_maintenance_odometer double precision,
    alert_before_km double precision,
    alert_before_days integer,
    is_active boolean,
    is_overdue boolean,
    notes text,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.maintenance_schedules OWNER TO uvis_user;

--
-- Name: COLUMN maintenance_schedules.vehicle_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.maintenance_schedules.vehicle_id IS '차량 ID';


--
-- Name: COLUMN maintenance_schedules.maintenance_type; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.maintenance_schedules.maintenance_type IS '정비 유형';


--
-- Name: COLUMN maintenance_schedules.interval_km; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.maintenance_schedules.interval_km IS '주행거리 주기(km)';


--
-- Name: COLUMN maintenance_schedules.interval_months; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.maintenance_schedules.interval_months IS '기간 주기(개월)';


--
-- Name: COLUMN maintenance_schedules.last_maintenance_date; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.maintenance_schedules.last_maintenance_date IS '마지막 정비일';


--
-- Name: COLUMN maintenance_schedules.last_maintenance_odometer; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.maintenance_schedules.last_maintenance_odometer IS '마지막 정비 시 주행거리';


--
-- Name: COLUMN maintenance_schedules.next_maintenance_date; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.maintenance_schedules.next_maintenance_date IS '다음 정비 예정일';


--
-- Name: COLUMN maintenance_schedules.next_maintenance_odometer; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.maintenance_schedules.next_maintenance_odometer IS '다음 정비 예정 주행거리';


--
-- Name: COLUMN maintenance_schedules.alert_before_km; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.maintenance_schedules.alert_before_km IS 'km 사전 알림';


--
-- Name: COLUMN maintenance_schedules.alert_before_days; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.maintenance_schedules.alert_before_days IS '일 사전 알림';


--
-- Name: COLUMN maintenance_schedules.is_active; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.maintenance_schedules.is_active IS '활성 여부';


--
-- Name: COLUMN maintenance_schedules.is_overdue; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.maintenance_schedules.is_overdue IS '연체 여부';


--
-- Name: COLUMN maintenance_schedules.notes; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.maintenance_schedules.notes IS '비고';


--
-- Name: maintenance_schedules_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.maintenance_schedules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.maintenance_schedules_id_seq OWNER TO uvis_user;

--
-- Name: maintenance_schedules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.maintenance_schedules_id_seq OWNED BY public.maintenance_schedules.id;


--
-- Name: notices; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.notices (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    content text NOT NULL,
    author character varying(100) NOT NULL,
    image_url character varying(500),
    is_important boolean,
    views integer,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.notices OWNER TO uvis_user;

--
-- Name: COLUMN notices.title; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notices.title IS '공지사항 제목';


--
-- Name: COLUMN notices.content; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notices.content IS '공지사항 내용';


--
-- Name: COLUMN notices.author; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notices.author IS '작성자';


--
-- Name: COLUMN notices.image_url; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notices.image_url IS '첨부 이미지 URL';


--
-- Name: COLUMN notices.is_important; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notices.is_important IS '중요 공지 여부';


--
-- Name: COLUMN notices.views; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notices.views IS '조회수';


--
-- Name: COLUMN notices.is_active; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notices.is_active IS '활성화 여부';


--
-- Name: COLUMN notices.created_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notices.created_at IS '생성일시';


--
-- Name: COLUMN notices.updated_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notices.updated_at IS '수정일시';


--
-- Name: notices_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.notices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.notices_id_seq OWNER TO uvis_user;

--
-- Name: notices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.notices_id_seq OWNED BY public.notices.id;


--
-- Name: notification_templates; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.notification_templates (
    id integer NOT NULL,
    template_code character varying(100) NOT NULL,
    template_name character varying(200) NOT NULL,
    notification_type public.notificationtype NOT NULL,
    channel public.notificationchannel NOT NULL,
    title_template character varying(200) NOT NULL,
    message_template text NOT NULL,
    kakao_template_id character varying(100),
    kakao_button_json json,
    description text,
    variables json,
    is_active boolean,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.notification_templates OWNER TO uvis_user;

--
-- Name: TABLE notification_templates; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON TABLE public.notification_templates IS '알림 템플릿';


--
-- Name: COLUMN notification_templates.id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notification_templates.id IS '템플릿ID';


--
-- Name: COLUMN notification_templates.template_code; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notification_templates.template_code IS '템플릿 코드';


--
-- Name: COLUMN notification_templates.template_name; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notification_templates.template_name IS '템플릿명';


--
-- Name: COLUMN notification_templates.notification_type; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notification_templates.notification_type IS '알림 유형';


--
-- Name: COLUMN notification_templates.channel; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notification_templates.channel IS '알림 채널';


--
-- Name: COLUMN notification_templates.title_template; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notification_templates.title_template IS '제목 템플릿';


--
-- Name: COLUMN notification_templates.message_template; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notification_templates.message_template IS '메시지 템플릿';


--
-- Name: COLUMN notification_templates.kakao_template_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notification_templates.kakao_template_id IS '카카오톡 템플릿 ID';


--
-- Name: COLUMN notification_templates.kakao_button_json; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notification_templates.kakao_button_json IS '카카오톡 버튼 (JSON)';


--
-- Name: COLUMN notification_templates.description; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notification_templates.description IS '템플릿 설명';


--
-- Name: COLUMN notification_templates.variables; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notification_templates.variables IS '변수 목록 (JSON)';


--
-- Name: COLUMN notification_templates.is_active; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notification_templates.is_active IS '사용 여부';


--
-- Name: COLUMN notification_templates.created_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notification_templates.created_at IS '생성일시';


--
-- Name: COLUMN notification_templates.updated_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notification_templates.updated_at IS '수정일시';


--
-- Name: notification_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.notification_templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.notification_templates_id_seq OWNER TO uvis_user;

--
-- Name: notification_templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.notification_templates_id_seq OWNED BY public.notification_templates.id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    notification_type public.notificationtype NOT NULL,
    channel public.notificationchannel NOT NULL,
    status public.notificationstatus NOT NULL,
    recipient_name character varying(100) NOT NULL,
    recipient_phone character varying(20),
    recipient_email character varying(200),
    recipient_device_token character varying(500),
    title character varying(200) NOT NULL,
    message text NOT NULL,
    template_code character varying(100),
    notification_metadata json,
    sent_at timestamp without time zone,
    delivered_at timestamp without time zone,
    read_at timestamp without time zone,
    external_id character varying(200),
    external_response json,
    error_message text,
    retry_count integer,
    order_id integer,
    dispatch_id integer,
    vehicle_id integer,
    driver_id integer,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone
);


ALTER TABLE public.notifications OWNER TO uvis_user;

--
-- Name: TABLE notifications; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON TABLE public.notifications IS '알림 이력';


--
-- Name: COLUMN notifications.id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.id IS '알림ID';


--
-- Name: COLUMN notifications.notification_type; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.notification_type IS '알림 유형';


--
-- Name: COLUMN notifications.channel; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.channel IS '알림 채널';


--
-- Name: COLUMN notifications.status; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.status IS '알림 상태';


--
-- Name: COLUMN notifications.recipient_name; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.recipient_name IS '수신자명';


--
-- Name: COLUMN notifications.recipient_phone; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.recipient_phone IS '수신자 전화번호';


--
-- Name: COLUMN notifications.recipient_email; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.recipient_email IS '수신자 이메일';


--
-- Name: COLUMN notifications.recipient_device_token; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.recipient_device_token IS '기기 토큰 (FCM)';


--
-- Name: COLUMN notifications.title; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.title IS '알림 제목';


--
-- Name: COLUMN notifications.message; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.message IS '알림 메시지';


--
-- Name: COLUMN notifications.template_code; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.template_code IS '템플릿 코드 (카카오톡)';


--
-- Name: COLUMN notifications.notification_metadata; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.notification_metadata IS '추가 메타데이터 (JSON)';


--
-- Name: COLUMN notifications.sent_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.sent_at IS '발송 시각';


--
-- Name: COLUMN notifications.delivered_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.delivered_at IS '전달 완료 시각';


--
-- Name: COLUMN notifications.read_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.read_at IS '읽음 시각';


--
-- Name: COLUMN notifications.external_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.external_id IS '외부 서비스 메시지 ID';


--
-- Name: COLUMN notifications.external_response; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.external_response IS '외부 서비스 응답';


--
-- Name: COLUMN notifications.error_message; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.error_message IS '에러 메시지';


--
-- Name: COLUMN notifications.retry_count; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.retry_count IS '재시도 횟수';


--
-- Name: COLUMN notifications.order_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.order_id IS '주문ID';


--
-- Name: COLUMN notifications.dispatch_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.dispatch_id IS '배차ID';


--
-- Name: COLUMN notifications.vehicle_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.vehicle_id IS '차량ID';


--
-- Name: COLUMN notifications.driver_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.driver_id IS '기사ID';


--
-- Name: COLUMN notifications.created_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.created_at IS '생성일시';


--
-- Name: COLUMN notifications.updated_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.notifications.updated_at IS '수정일시';


--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.notifications_id_seq OWNER TO uvis_user;

--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: order_templates; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.order_templates (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    category character varying(50),
    temperature_zone character varying(20) NOT NULL,
    pickup_client_id integer,
    pickup_address character varying(500),
    pickup_address_detail character varying(200),
    delivery_client_id integer,
    delivery_address character varying(500),
    delivery_address_detail character varying(200),
    pallet_count integer NOT NULL,
    weight_kg double precision,
    volume_cbm double precision,
    product_name character varying(200),
    product_code character varying(100),
    pickup_start_time character varying(5),
    pickup_end_time character varying(5),
    delivery_start_time character varying(5),
    delivery_end_time character varying(5),
    requires_forklift boolean,
    is_stackable boolean,
    priority integer,
    notes text,
    usage_count integer,
    last_used_at timestamp with time zone,
    is_shared boolean,
    created_by integer,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.order_templates OWNER TO uvis_user;

--
-- Name: COLUMN order_templates.name; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.name IS '템플릿 이름';


--
-- Name: COLUMN order_templates.description; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.description IS '템플릿 설명';


--
-- Name: COLUMN order_templates.category; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.category IS '카테고리 (예: 정기배송, 긴급, 장거리)';


--
-- Name: COLUMN order_templates.pickup_client_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.pickup_client_id IS '상차 거래처 ID';


--
-- Name: COLUMN order_templates.pickup_address; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.pickup_address IS '상차 주소';


--
-- Name: COLUMN order_templates.pickup_address_detail; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.pickup_address_detail IS '상차 상세주소';


--
-- Name: COLUMN order_templates.delivery_client_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.delivery_client_id IS '하차 거래처 ID';


--
-- Name: COLUMN order_templates.delivery_address; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.delivery_address IS '하차 주소';


--
-- Name: COLUMN order_templates.delivery_address_detail; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.delivery_address_detail IS '하차 상세주소';


--
-- Name: COLUMN order_templates.pallet_count; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.pallet_count IS '팔레트 수';


--
-- Name: COLUMN order_templates.weight_kg; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.weight_kg IS '중량(kg)';


--
-- Name: COLUMN order_templates.volume_cbm; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.volume_cbm IS '용적(CBM)';


--
-- Name: COLUMN order_templates.product_name; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.product_name IS '품목명';


--
-- Name: COLUMN order_templates.product_code; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.product_code IS '품목코드';


--
-- Name: COLUMN order_templates.pickup_start_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.pickup_start_time IS '상차 시작 시간 (HH:MM)';


--
-- Name: COLUMN order_templates.pickup_end_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.pickup_end_time IS '상차 종료 시간 (HH:MM)';


--
-- Name: COLUMN order_templates.delivery_start_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.delivery_start_time IS '하차 시작 시간 (HH:MM)';


--
-- Name: COLUMN order_templates.delivery_end_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.delivery_end_time IS '하차 종료 시간 (HH:MM)';


--
-- Name: COLUMN order_templates.requires_forklift; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.requires_forklift IS '지게차 필요 여부';


--
-- Name: COLUMN order_templates.is_stackable; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.is_stackable IS '적재 가능 여부';


--
-- Name: COLUMN order_templates.priority; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.priority IS '우선순위 (1-10)';


--
-- Name: COLUMN order_templates.notes; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.notes IS '비고';


--
-- Name: COLUMN order_templates.usage_count; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.usage_count IS '사용 횟수';


--
-- Name: COLUMN order_templates.last_used_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.last_used_at IS '마지막 사용 시간';


--
-- Name: COLUMN order_templates.is_shared; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.is_shared IS '공유 여부 (모든 사용자가 사용 가능)';


--
-- Name: COLUMN order_templates.created_by; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.created_by IS '생성자 User ID';


--
-- Name: COLUMN order_templates.is_active; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.is_active IS '활성화 여부';


--
-- Name: COLUMN order_templates.created_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.created_at IS '생성 시간';


--
-- Name: COLUMN order_templates.updated_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.order_templates.updated_at IS '수정 시간';


--
-- Name: order_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.order_templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.order_templates_id_seq OWNER TO uvis_user;

--
-- Name: order_templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.order_templates_id_seq OWNED BY public.order_templates.id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.orders (
    order_number character varying(50) NOT NULL,
    order_date date NOT NULL,
    temperature_zone public.temperaturezone NOT NULL,
    pickup_client_id integer,
    delivery_client_id integer,
    pickup_address character varying(500),
    pickup_address_detail character varying(200),
    pickup_latitude double precision,
    pickup_longitude double precision,
    delivery_address character varying(500),
    delivery_address_detail character varying(200),
    delivery_latitude double precision,
    delivery_longitude double precision,
    pallet_count integer NOT NULL,
    weight_kg double precision,
    volume_cbm double precision,
    product_name character varying(200),
    product_code character varying(100),
    pickup_start_time time without time zone,
    pickup_end_time time without time zone,
    delivery_start_time time without time zone,
    delivery_end_time time without time zone,
    requested_delivery_date date,
    is_reserved boolean NOT NULL,
    reserved_at date,
    confirmed_at date,
    recurring_type character varying(20),
    recurring_end_date date,
    priority integer NOT NULL,
    requires_forklift boolean NOT NULL,
    is_stackable boolean NOT NULL,
    status public.orderstatus NOT NULL,
    notes text,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.orders OWNER TO uvis_user;

--
-- Name: COLUMN orders.order_number; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.order_number IS '주문번호';


--
-- Name: COLUMN orders.order_date; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.order_date IS '주문일자';


--
-- Name: COLUMN orders.temperature_zone; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.temperature_zone IS '온도대 구분';


--
-- Name: COLUMN orders.pickup_client_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.pickup_client_id IS '상차 거래처 ID';


--
-- Name: COLUMN orders.delivery_client_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.delivery_client_id IS '하차 거래처 ID';


--
-- Name: COLUMN orders.pickup_address; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.pickup_address IS '상차 주소';


--
-- Name: COLUMN orders.pickup_address_detail; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.pickup_address_detail IS '상차 상세주소';


--
-- Name: COLUMN orders.pickup_latitude; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.pickup_latitude IS '상차 위도';


--
-- Name: COLUMN orders.pickup_longitude; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.pickup_longitude IS '상차 경도';


--
-- Name: COLUMN orders.delivery_address; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.delivery_address IS '하차 주소';


--
-- Name: COLUMN orders.delivery_address_detail; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.delivery_address_detail IS '하차 상세주소';


--
-- Name: COLUMN orders.delivery_latitude; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.delivery_latitude IS '하차 위도';


--
-- Name: COLUMN orders.delivery_longitude; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.delivery_longitude IS '하차 경도';


--
-- Name: COLUMN orders.pallet_count; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.pallet_count IS '팔레트 수';


--
-- Name: COLUMN orders.weight_kg; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.weight_kg IS '중량(kg) - Deprecated';


--
-- Name: COLUMN orders.volume_cbm; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.volume_cbm IS '용적(CBM)';


--
-- Name: COLUMN orders.product_name; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.product_name IS '품목명';


--
-- Name: COLUMN orders.product_code; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.product_code IS '품목코드';


--
-- Name: COLUMN orders.pickup_start_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.pickup_start_time IS '상차 시작시간';


--
-- Name: COLUMN orders.pickup_end_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.pickup_end_time IS '상차 종료시간';


--
-- Name: COLUMN orders.delivery_start_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.delivery_start_time IS '하차 시작시간';


--
-- Name: COLUMN orders.delivery_end_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.delivery_end_time IS '하차 종료시간';


--
-- Name: COLUMN orders.requested_delivery_date; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.requested_delivery_date IS '희망 배송일';


--
-- Name: COLUMN orders.is_reserved; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.is_reserved IS '예약 오더 여부';


--
-- Name: COLUMN orders.reserved_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.reserved_at IS '예약 생성일';


--
-- Name: COLUMN orders.confirmed_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.confirmed_at IS '오더 확정일';


--
-- Name: COLUMN orders.recurring_type; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.recurring_type IS '반복 유형 (DAILY, WEEKLY, MONTHLY)';


--
-- Name: COLUMN orders.recurring_end_date; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.recurring_end_date IS '반복 종료일';


--
-- Name: COLUMN orders.priority; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.priority IS '우선순위(1:높음 ~ 10:낮음)';


--
-- Name: COLUMN orders.requires_forklift; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.requires_forklift IS '지게차 필요 여부';


--
-- Name: COLUMN orders.is_stackable; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.is_stackable IS '적재 가능 여부';


--
-- Name: COLUMN orders.status; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.status IS '주문 상태';


--
-- Name: COLUMN orders.notes; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.orders.notes IS '특이사항';


--
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.orders_id_seq OWNER TO uvis_user;

--
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.orders_id_seq OWNED BY public.orders.id;


--
-- Name: payments; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.payments (
    id integer NOT NULL,
    payment_number character varying(50) NOT NULL,
    invoice_id integer NOT NULL,
    amount double precision NOT NULL,
    payment_method public.paymentmethod NOT NULL,
    payment_date date NOT NULL,
    reference_number character varying(100),
    bank_name character varying(100),
    account_number character varying(100),
    notes text,
    receipt_url character varying(500),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    created_by integer
);


ALTER TABLE public.payments OWNER TO uvis_user;

--
-- Name: payments_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.payments_id_seq OWNER TO uvis_user;

--
-- Name: payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.payments_id_seq OWNED BY public.payments.id;


--
-- Name: purchase_orders; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.purchase_orders (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    content text,
    image_urls text,
    author character varying(100) NOT NULL,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.purchase_orders OWNER TO uvis_user;

--
-- Name: COLUMN purchase_orders.title; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.purchase_orders.title IS '발주서 제목';


--
-- Name: COLUMN purchase_orders.content; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.purchase_orders.content IS '발주 내용';


--
-- Name: COLUMN purchase_orders.image_urls; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.purchase_orders.image_urls IS '첨부 이미지 URL 목록 (JSON 배열, 최대 5개)';


--
-- Name: COLUMN purchase_orders.author; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.purchase_orders.author IS '작성자';


--
-- Name: COLUMN purchase_orders.is_active; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.purchase_orders.is_active IS '활성화 여부';


--
-- Name: COLUMN purchase_orders.created_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.purchase_orders.created_at IS '생성일시';


--
-- Name: COLUMN purchase_orders.updated_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.purchase_orders.updated_at IS '수정일시';


--
-- Name: purchase_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.purchase_orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.purchase_orders_id_seq OWNER TO uvis_user;

--
-- Name: purchase_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.purchase_orders_id_seq OWNED BY public.purchase_orders.id;


--
-- Name: push_notification_logs; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.push_notification_logs (
    id integer NOT NULL,
    user_id integer,
    token character varying(255),
    title character varying(255) NOT NULL,
    body character varying(1000) NOT NULL,
    data_json character varying(2000),
    notification_type character varying(50),
    status character varying(20),
    error_message character varying(500),
    sent_at timestamp without time zone
);


ALTER TABLE public.push_notification_logs OWNER TO uvis_user;

--
-- Name: push_notification_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.push_notification_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.push_notification_logs_id_seq OWNER TO uvis_user;

--
-- Name: push_notification_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.push_notification_logs_id_seq OWNED BY public.push_notification_logs.id;


--
-- Name: recurring_orders; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.recurring_orders (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    frequency public.recurringfrequency NOT NULL,
    start_date date NOT NULL,
    end_date date,
    weekdays integer,
    day_of_month integer,
    temperature_zone public.temperaturezone NOT NULL,
    pickup_client_id integer,
    delivery_client_id integer,
    pickup_address character varying(500),
    pickup_address_detail character varying(200),
    delivery_address character varying(500),
    delivery_address_detail character varying(200),
    pallet_count integer NOT NULL,
    weight_kg integer,
    volume_cbm integer,
    product_name character varying(200),
    product_code character varying(100),
    pickup_start_time time without time zone,
    pickup_end_time time without time zone,
    delivery_start_time time without time zone,
    delivery_end_time time without time zone,
    priority integer,
    requires_forklift boolean,
    is_stackable boolean,
    notes text,
    is_active boolean,
    last_generated_date date,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.recurring_orders OWNER TO uvis_user;

--
-- Name: COLUMN recurring_orders.name; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.recurring_orders.name IS '정기 주문명';


--
-- Name: COLUMN recurring_orders.description; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.recurring_orders.description IS '설명';


--
-- Name: COLUMN recurring_orders.frequency; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.recurring_orders.frequency IS '반복 주기';


--
-- Name: COLUMN recurring_orders.start_date; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.recurring_orders.start_date IS '시작일';


--
-- Name: COLUMN recurring_orders.end_date; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.recurring_orders.end_date IS '종료일 (null이면 무제한)';


--
-- Name: COLUMN recurring_orders.weekdays; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.recurring_orders.weekdays IS '실행 요일 (비트 플래그)';


--
-- Name: COLUMN recurring_orders.day_of_month; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.recurring_orders.day_of_month IS '매월 특정일 (1-31)';


--
-- Name: COLUMN recurring_orders.is_active; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.recurring_orders.is_active IS '활성화 여부';


--
-- Name: COLUMN recurring_orders.last_generated_date; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.recurring_orders.last_generated_date IS '마지막 생성일';


--
-- Name: recurring_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.recurring_orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.recurring_orders_id_seq OWNER TO uvis_user;

--
-- Name: recurring_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.recurring_orders_id_seq OWNED BY public.recurring_orders.id;


--
-- Name: security_alerts; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.security_alerts (
    id integer NOT NULL,
    user_id integer,
    alert_type character varying(50) NOT NULL,
    severity character varying(20),
    description character varying(500) NOT NULL,
    ip_address character varying(50),
    user_agent character varying(255),
    is_resolved boolean,
    resolved_by integer,
    resolved_at timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.security_alerts OWNER TO uvis_user;

--
-- Name: security_alerts_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.security_alerts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.security_alerts_id_seq OWNER TO uvis_user;

--
-- Name: security_alerts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.security_alerts_id_seq OWNED BY public.security_alerts.id;


--
-- Name: temperature_alerts; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.temperature_alerts (
    id integer NOT NULL,
    vehicle_id integer NOT NULL,
    dispatch_id integer,
    location_id integer,
    alert_type character varying(50) NOT NULL,
    severity character varying(20) NOT NULL,
    temperature_celsius double precision NOT NULL,
    threshold_min double precision,
    threshold_max double precision,
    detected_at timestamp without time zone NOT NULL,
    resolved_at timestamp without time zone,
    is_resolved boolean,
    notification_sent boolean,
    notification_channels character varying(200),
    message text,
    notes text
);


ALTER TABLE public.temperature_alerts OWNER TO uvis_user;

--
-- Name: temperature_alerts_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.temperature_alerts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.temperature_alerts_id_seq OWNER TO uvis_user;

--
-- Name: temperature_alerts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.temperature_alerts_id_seq OWNED BY public.temperature_alerts.id;


--
-- Name: two_factor_auth; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.two_factor_auth (
    id integer NOT NULL,
    user_id integer NOT NULL,
    secret_key character varying(32) NOT NULL,
    is_enabled boolean,
    backup_codes character varying(500),
    created_at timestamp without time zone,
    last_used_at timestamp without time zone
);


ALTER TABLE public.two_factor_auth OWNER TO uvis_user;

--
-- Name: two_factor_auth_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.two_factor_auth_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.two_factor_auth_id_seq OWNER TO uvis_user;

--
-- Name: two_factor_auth_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.two_factor_auth_id_seq OWNED BY public.two_factor_auth.id;


--
-- Name: two_factor_logs; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.two_factor_logs (
    id integer NOT NULL,
    user_id integer NOT NULL,
    action character varying(50) NOT NULL,
    ip_address character varying(50),
    user_agent character varying(255),
    success boolean,
    created_at timestamp without time zone
);


ALTER TABLE public.two_factor_logs OWNER TO uvis_user;

--
-- Name: two_factor_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.two_factor_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.two_factor_logs_id_seq OWNER TO uvis_user;

--
-- Name: two_factor_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.two_factor_logs_id_seq OWNED BY public.two_factor_logs.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    full_name character varying(100),
    role public.userrole NOT NULL,
    is_active boolean NOT NULL,
    is_superuser boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    last_login timestamp with time zone
);


ALTER TABLE public.users OWNER TO uvis_user;

--
-- Name: COLUMN users.id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.users.id IS 'ID';


--
-- Name: COLUMN users.username; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.users.username IS '사용자명';


--
-- Name: COLUMN users.email; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.users.email IS '이메일';


--
-- Name: COLUMN users.hashed_password; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.users.hashed_password IS '해시된 비밀번호';


--
-- Name: COLUMN users.full_name; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.users.full_name IS '전체 이름';


--
-- Name: COLUMN users.role; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.users.role IS '사용자 역할';


--
-- Name: COLUMN users.is_active; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.users.is_active IS '활성 상태';


--
-- Name: COLUMN users.is_superuser; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.users.is_superuser IS '슈퍼유저 여부';


--
-- Name: COLUMN users.created_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.users.created_at IS '생성일시';


--
-- Name: COLUMN users.updated_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.users.updated_at IS '수정일시';


--
-- Name: COLUMN users.last_login; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.users.last_login IS '마지막 로그인';


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO uvis_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: uvis_access_keys; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.uvis_access_keys (
    id integer NOT NULL,
    serial_key character varying(50) NOT NULL,
    access_key character varying(100) NOT NULL,
    issued_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone NOT NULL,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.uvis_access_keys OWNER TO uvis_user;

--
-- Name: COLUMN uvis_access_keys.id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.uvis_access_keys.id IS 'ID';


--
-- Name: COLUMN uvis_access_keys.serial_key; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.uvis_access_keys.serial_key IS '업체 인증키';


--
-- Name: COLUMN uvis_access_keys.access_key; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.uvis_access_keys.access_key IS '실시간 인증키';


--
-- Name: COLUMN uvis_access_keys.issued_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.uvis_access_keys.issued_at IS '발급 시간';


--
-- Name: COLUMN uvis_access_keys.expires_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.uvis_access_keys.expires_at IS '만료 시간 (발급 후 5분)';


--
-- Name: COLUMN uvis_access_keys.is_active; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.uvis_access_keys.is_active IS '활성화 여부';


--
-- Name: COLUMN uvis_access_keys.created_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.uvis_access_keys.created_at IS '생성일시';


--
-- Name: COLUMN uvis_access_keys.updated_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.uvis_access_keys.updated_at IS '수정일시';


--
-- Name: uvis_access_keys_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.uvis_access_keys_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.uvis_access_keys_id_seq OWNER TO uvis_user;

--
-- Name: uvis_access_keys_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.uvis_access_keys_id_seq OWNED BY public.uvis_access_keys.id;


--
-- Name: uvis_api_logs; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.uvis_api_logs (
    id integer NOT NULL,
    api_type character varying(20) NOT NULL,
    method character varying(10) NOT NULL,
    url text NOT NULL,
    request_params text,
    response_status integer,
    response_data text,
    error_message text,
    execution_time_ms integer,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.uvis_api_logs OWNER TO uvis_user;

--
-- Name: COLUMN uvis_api_logs.id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.uvis_api_logs.id IS 'ID';


--
-- Name: COLUMN uvis_api_logs.api_type; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.uvis_api_logs.api_type IS 'API 유형 (auth/gps/temperature)';


--
-- Name: COLUMN uvis_api_logs.method; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.uvis_api_logs.method IS 'HTTP 메서드';


--
-- Name: COLUMN uvis_api_logs.url; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.uvis_api_logs.url IS '요청 URL';


--
-- Name: COLUMN uvis_api_logs.request_params; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.uvis_api_logs.request_params IS '요청 파라미터 (JSON)';


--
-- Name: COLUMN uvis_api_logs.response_status; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.uvis_api_logs.response_status IS '응답 상태 코드';


--
-- Name: COLUMN uvis_api_logs.response_data; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.uvis_api_logs.response_data IS '응답 데이터 (JSON)';


--
-- Name: COLUMN uvis_api_logs.error_message; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.uvis_api_logs.error_message IS '에러 메시지';


--
-- Name: COLUMN uvis_api_logs.execution_time_ms; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.uvis_api_logs.execution_time_ms IS '실행 시간 (ms)';


--
-- Name: COLUMN uvis_api_logs.created_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.uvis_api_logs.created_at IS '생성일시';


--
-- Name: uvis_api_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.uvis_api_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.uvis_api_logs_id_seq OWNER TO uvis_user;

--
-- Name: uvis_api_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.uvis_api_logs_id_seq OWNED BY public.uvis_api_logs.id;


--
-- Name: vehicle_gps_logs; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.vehicle_gps_logs (
    id integer NOT NULL,
    vehicle_id integer,
    tid_id character varying(11) NOT NULL,
    bi_date character varying(8) NOT NULL,
    bi_time character varying(6) NOT NULL,
    cm_number character varying(30),
    bi_turn_onoff character varying(3),
    bi_x_position character varying(10) NOT NULL,
    bi_y_position character varying(10) NOT NULL,
    bi_gps_speed integer,
    latitude double precision,
    longitude double precision,
    is_engine_on boolean,
    speed_kmh integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.vehicle_gps_logs OWNER TO uvis_user;

--
-- Name: COLUMN vehicle_gps_logs.id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_gps_logs.id IS 'ID';


--
-- Name: COLUMN vehicle_gps_logs.vehicle_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_gps_logs.vehicle_id IS '차량 ID';


--
-- Name: COLUMN vehicle_gps_logs.tid_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_gps_logs.tid_id IS '단말기 ID';


--
-- Name: COLUMN vehicle_gps_logs.bi_date; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_gps_logs.bi_date IS '날짜 (YYYYMMDD)';


--
-- Name: COLUMN vehicle_gps_logs.bi_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_gps_logs.bi_time IS '시간 (HHMMSS)';


--
-- Name: COLUMN vehicle_gps_logs.cm_number; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_gps_logs.cm_number IS '차량번호';


--
-- Name: COLUMN vehicle_gps_logs.bi_turn_onoff; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_gps_logs.bi_turn_onoff IS '시동 on/off';


--
-- Name: COLUMN vehicle_gps_logs.bi_x_position; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_gps_logs.bi_x_position IS '위도';


--
-- Name: COLUMN vehicle_gps_logs.bi_y_position; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_gps_logs.bi_y_position IS '경도';


--
-- Name: COLUMN vehicle_gps_logs.bi_gps_speed; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_gps_logs.bi_gps_speed IS '속도 (km/h)';


--
-- Name: COLUMN vehicle_gps_logs.latitude; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_gps_logs.latitude IS '위도 (Float)';


--
-- Name: COLUMN vehicle_gps_logs.longitude; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_gps_logs.longitude IS '경도 (Float)';


--
-- Name: COLUMN vehicle_gps_logs.is_engine_on; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_gps_logs.is_engine_on IS '시동 상태';


--
-- Name: COLUMN vehicle_gps_logs.speed_kmh; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_gps_logs.speed_kmh IS '속도 (km/h)';


--
-- Name: COLUMN vehicle_gps_logs.created_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_gps_logs.created_at IS '생성일시';


--
-- Name: COLUMN vehicle_gps_logs.updated_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_gps_logs.updated_at IS '수정일시';


--
-- Name: vehicle_gps_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.vehicle_gps_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vehicle_gps_logs_id_seq OWNER TO uvis_user;

--
-- Name: vehicle_gps_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.vehicle_gps_logs_id_seq OWNED BY public.vehicle_gps_logs.id;


--
-- Name: vehicle_inspections; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.vehicle_inspections (
    vehicle_id integer NOT NULL,
    inspection_type character varying(100) NOT NULL,
    inspection_date date NOT NULL,
    expiry_date date NOT NULL,
    result character varying(50),
    pass_status boolean,
    inspection_center character varying(200),
    inspector_name character varying(100),
    inspection_cost double precision,
    certificate_number character varying(100),
    certificate_file_path character varying(500),
    findings text,
    defects text,
    recommendations text,
    notes text,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.vehicle_inspections OWNER TO uvis_user;

--
-- Name: COLUMN vehicle_inspections.vehicle_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_inspections.vehicle_id IS '차량 ID';


--
-- Name: COLUMN vehicle_inspections.inspection_type; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_inspections.inspection_type IS '검사 유형 (정기검사, 종합검사 등)';


--
-- Name: COLUMN vehicle_inspections.inspection_date; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_inspections.inspection_date IS '검사일';


--
-- Name: COLUMN vehicle_inspections.expiry_date; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_inspections.expiry_date IS '만료일';


--
-- Name: COLUMN vehicle_inspections.result; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_inspections.result IS '검사 결과 (합격/불합격)';


--
-- Name: COLUMN vehicle_inspections.pass_status; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_inspections.pass_status IS '합격 여부';


--
-- Name: COLUMN vehicle_inspections.inspection_center; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_inspections.inspection_center IS '검사소명';


--
-- Name: COLUMN vehicle_inspections.inspector_name; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_inspections.inspector_name IS '검사자';


--
-- Name: COLUMN vehicle_inspections.inspection_cost; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_inspections.inspection_cost IS '검사 비용';


--
-- Name: COLUMN vehicle_inspections.certificate_number; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_inspections.certificate_number IS '검사증 번호';


--
-- Name: COLUMN vehicle_inspections.certificate_file_path; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_inspections.certificate_file_path IS '검사증 파일';


--
-- Name: COLUMN vehicle_inspections.findings; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_inspections.findings IS '발견사항';


--
-- Name: COLUMN vehicle_inspections.defects; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_inspections.defects IS '결함 사항';


--
-- Name: COLUMN vehicle_inspections.recommendations; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_inspections.recommendations IS '권고사항';


--
-- Name: COLUMN vehicle_inspections.notes; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_inspections.notes IS '비고';


--
-- Name: vehicle_inspections_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.vehicle_inspections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vehicle_inspections_id_seq OWNER TO uvis_user;

--
-- Name: vehicle_inspections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.vehicle_inspections_id_seq OWNED BY public.vehicle_inspections.id;


--
-- Name: vehicle_locations; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.vehicle_locations (
    id integer NOT NULL,
    vehicle_id integer NOT NULL,
    dispatch_id integer,
    latitude double precision NOT NULL,
    longitude double precision NOT NULL,
    accuracy double precision,
    altitude double precision,
    speed double precision,
    heading double precision,
    temperature_celsius double precision,
    humidity_percent double precision,
    uvis_device_id character varying(100),
    uvis_timestamp timestamp without time zone,
    recorded_at timestamp without time zone NOT NULL,
    is_ignition_on boolean,
    battery_voltage double precision,
    fuel_level_percent double precision,
    odometer_km double precision,
    address character varying(500),
    notes text
);


ALTER TABLE public.vehicle_locations OWNER TO uvis_user;

--
-- Name: vehicle_locations_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.vehicle_locations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vehicle_locations_id_seq OWNER TO uvis_user;

--
-- Name: vehicle_locations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.vehicle_locations_id_seq OWNED BY public.vehicle_locations.id;


--
-- Name: vehicle_maintenance_records; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.vehicle_maintenance_records (
    maintenance_number character varying(50) NOT NULL,
    vehicle_id integer NOT NULL,
    maintenance_type public.maintenancetype NOT NULL,
    status public.maintenancestatus NOT NULL,
    priority public.maintenancepriority NOT NULL,
    scheduled_date date NOT NULL,
    started_at timestamp without time zone,
    completed_at timestamp without time zone,
    odometer_reading double precision,
    service_center character varying(200),
    service_center_contact character varying(50),
    service_center_address character varying(500),
    mechanic_name character varying(100),
    assigned_by character varying(100),
    labor_cost double precision,
    parts_cost double precision,
    total_cost double precision,
    description text,
    findings text,
    recommendations text,
    notes text,
    invoice_number character varying(100),
    invoice_file_path character varying(500),
    before_photos text,
    after_photos text,
    next_maintenance_date date,
    next_maintenance_odometer double precision,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.vehicle_maintenance_records OWNER TO uvis_user;

--
-- Name: COLUMN vehicle_maintenance_records.maintenance_number; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.maintenance_number IS '정비 번호';


--
-- Name: COLUMN vehicle_maintenance_records.vehicle_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.vehicle_id IS '차량 ID';


--
-- Name: COLUMN vehicle_maintenance_records.maintenance_type; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.maintenance_type IS '정비 유형';


--
-- Name: COLUMN vehicle_maintenance_records.status; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.status IS '상태';


--
-- Name: COLUMN vehicle_maintenance_records.priority; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.priority IS '우선순위';


--
-- Name: COLUMN vehicle_maintenance_records.scheduled_date; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.scheduled_date IS '예정일';


--
-- Name: COLUMN vehicle_maintenance_records.started_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.started_at IS '시작 시각';


--
-- Name: COLUMN vehicle_maintenance_records.completed_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.completed_at IS '완료 시각';


--
-- Name: COLUMN vehicle_maintenance_records.odometer_reading; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.odometer_reading IS '주행거리(km)';


--
-- Name: COLUMN vehicle_maintenance_records.service_center; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.service_center IS '정비소명';


--
-- Name: COLUMN vehicle_maintenance_records.service_center_contact; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.service_center_contact IS '정비소 연락처';


--
-- Name: COLUMN vehicle_maintenance_records.service_center_address; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.service_center_address IS '정비소 주소';


--
-- Name: COLUMN vehicle_maintenance_records.mechanic_name; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.mechanic_name IS '정비사 이름';


--
-- Name: COLUMN vehicle_maintenance_records.assigned_by; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.assigned_by IS '지시자';


--
-- Name: COLUMN vehicle_maintenance_records.labor_cost; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.labor_cost IS '인건비';


--
-- Name: COLUMN vehicle_maintenance_records.parts_cost; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.parts_cost IS '부품비';


--
-- Name: COLUMN vehicle_maintenance_records.total_cost; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.total_cost IS '총 비용';


--
-- Name: COLUMN vehicle_maintenance_records.description; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.description IS '정비 내용';


--
-- Name: COLUMN vehicle_maintenance_records.findings; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.findings IS '발견사항';


--
-- Name: COLUMN vehicle_maintenance_records.recommendations; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.recommendations IS '권고사항';


--
-- Name: COLUMN vehicle_maintenance_records.notes; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.notes IS '비고';


--
-- Name: COLUMN vehicle_maintenance_records.invoice_number; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.invoice_number IS '청구서 번호';


--
-- Name: COLUMN vehicle_maintenance_records.invoice_file_path; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.invoice_file_path IS '청구서 파일';


--
-- Name: COLUMN vehicle_maintenance_records.before_photos; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.before_photos IS '작업 전 사진 (JSON array)';


--
-- Name: COLUMN vehicle_maintenance_records.after_photos; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.after_photos IS '작업 후 사진 (JSON array)';


--
-- Name: COLUMN vehicle_maintenance_records.next_maintenance_date; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.next_maintenance_date IS '다음 정비 예정일';


--
-- Name: COLUMN vehicle_maintenance_records.next_maintenance_odometer; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_maintenance_records.next_maintenance_odometer IS '다음 정비 주행거리';


--
-- Name: vehicle_maintenance_records_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.vehicle_maintenance_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vehicle_maintenance_records_id_seq OWNER TO uvis_user;

--
-- Name: vehicle_maintenance_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.vehicle_maintenance_records_id_seq OWNED BY public.vehicle_maintenance_records.id;


--
-- Name: vehicle_parts; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.vehicle_parts (
    part_number character varying(100) NOT NULL,
    part_name character varying(200) NOT NULL,
    category public.partcategory NOT NULL,
    manufacturer character varying(200),
    model character varying(200),
    quantity_in_stock integer,
    minimum_stock integer,
    unit character varying(20),
    unit_price double precision NOT NULL,
    supplier character varying(200),
    supplier_contact character varying(50),
    compatible_models text,
    average_lifespan_km double precision,
    average_lifespan_months integer,
    description text,
    notes text,
    is_active boolean,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.vehicle_parts OWNER TO uvis_user;

--
-- Name: COLUMN vehicle_parts.part_number; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_parts.part_number IS '부품 번호';


--
-- Name: COLUMN vehicle_parts.part_name; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_parts.part_name IS '부품명';


--
-- Name: COLUMN vehicle_parts.category; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_parts.category IS '카테고리';


--
-- Name: COLUMN vehicle_parts.manufacturer; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_parts.manufacturer IS '제조사';


--
-- Name: COLUMN vehicle_parts.model; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_parts.model IS '모델';


--
-- Name: COLUMN vehicle_parts.quantity_in_stock; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_parts.quantity_in_stock IS '재고 수량';


--
-- Name: COLUMN vehicle_parts.minimum_stock; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_parts.minimum_stock IS '최소 재고';


--
-- Name: COLUMN vehicle_parts.unit; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_parts.unit IS '단위';


--
-- Name: COLUMN vehicle_parts.unit_price; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_parts.unit_price IS '단가';


--
-- Name: COLUMN vehicle_parts.supplier; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_parts.supplier IS '공급업체';


--
-- Name: COLUMN vehicle_parts.supplier_contact; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_parts.supplier_contact IS '공급업체 연락처';


--
-- Name: COLUMN vehicle_parts.compatible_models; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_parts.compatible_models IS '호환 차량 모델 (JSON array)';


--
-- Name: COLUMN vehicle_parts.average_lifespan_km; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_parts.average_lifespan_km IS '평균 수명(km)';


--
-- Name: COLUMN vehicle_parts.average_lifespan_months; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_parts.average_lifespan_months IS '평균 수명(개월)';


--
-- Name: COLUMN vehicle_parts.description; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_parts.description IS '설명';


--
-- Name: COLUMN vehicle_parts.notes; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_parts.notes IS '비고';


--
-- Name: COLUMN vehicle_parts.is_active; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_parts.is_active IS '활성 여부';


--
-- Name: vehicle_parts_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.vehicle_parts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vehicle_parts_id_seq OWNER TO uvis_user;

--
-- Name: vehicle_parts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.vehicle_parts_id_seq OWNED BY public.vehicle_parts.id;


--
-- Name: vehicle_temperature_logs; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.vehicle_temperature_logs (
    id integer NOT NULL,
    vehicle_id integer,
    off_key character varying(7),
    tid_id character varying(11) NOT NULL,
    tpl_date character varying(8) NOT NULL,
    tpl_time character varying(6) NOT NULL,
    cm_number character varying(30),
    tpl_x_position character varying(10),
    tpl_y_position character varying(10),
    tpl_signal_a integer,
    tpl_degree_a character varying(5),
    temperature_a double precision,
    tpl_signal_b integer,
    tpl_degree_b character varying(5),
    temperature_b double precision,
    latitude double precision,
    longitude double precision,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.vehicle_temperature_logs OWNER TO uvis_user;

--
-- Name: COLUMN vehicle_temperature_logs.id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_temperature_logs.id IS 'ID';


--
-- Name: COLUMN vehicle_temperature_logs.vehicle_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_temperature_logs.vehicle_id IS '차량 ID';


--
-- Name: COLUMN vehicle_temperature_logs.off_key; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_temperature_logs.off_key IS '고객 코드';


--
-- Name: COLUMN vehicle_temperature_logs.tid_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_temperature_logs.tid_id IS '단말기 ID';


--
-- Name: COLUMN vehicle_temperature_logs.tpl_date; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_temperature_logs.tpl_date IS '날짜 (YYYYMMDD)';


--
-- Name: COLUMN vehicle_temperature_logs.tpl_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_temperature_logs.tpl_time IS '시간 (HHMMSS)';


--
-- Name: COLUMN vehicle_temperature_logs.cm_number; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_temperature_logs.cm_number IS '차량번호';


--
-- Name: COLUMN vehicle_temperature_logs.tpl_x_position; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_temperature_logs.tpl_x_position IS '위도';


--
-- Name: COLUMN vehicle_temperature_logs.tpl_y_position; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_temperature_logs.tpl_y_position IS '경도';


--
-- Name: COLUMN vehicle_temperature_logs.tpl_signal_a; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_temperature_logs.tpl_signal_a IS 'A 온도 부호 (0=''+'', 1=''-'')';


--
-- Name: COLUMN vehicle_temperature_logs.tpl_degree_a; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_temperature_logs.tpl_degree_a IS 'A 온도값';


--
-- Name: COLUMN vehicle_temperature_logs.temperature_a; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_temperature_logs.temperature_a IS 'A 온도 (℃)';


--
-- Name: COLUMN vehicle_temperature_logs.tpl_signal_b; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_temperature_logs.tpl_signal_b IS 'B 온도 부호 (0=''+'', 1=''-'')';


--
-- Name: COLUMN vehicle_temperature_logs.tpl_degree_b; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_temperature_logs.tpl_degree_b IS 'B 온도값';


--
-- Name: COLUMN vehicle_temperature_logs.temperature_b; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_temperature_logs.temperature_b IS 'B 온도 (℃)';


--
-- Name: COLUMN vehicle_temperature_logs.latitude; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_temperature_logs.latitude IS '위도 (Float)';


--
-- Name: COLUMN vehicle_temperature_logs.longitude; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_temperature_logs.longitude IS '경도 (Float)';


--
-- Name: COLUMN vehicle_temperature_logs.created_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_temperature_logs.created_at IS '생성일시';


--
-- Name: COLUMN vehicle_temperature_logs.updated_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicle_temperature_logs.updated_at IS '수정일시';


--
-- Name: vehicle_temperature_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.vehicle_temperature_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vehicle_temperature_logs_id_seq OWNER TO uvis_user;

--
-- Name: vehicle_temperature_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.vehicle_temperature_logs_id_seq OWNED BY public.vehicle_temperature_logs.id;


--
-- Name: vehicles; Type: TABLE; Schema: public; Owner: uvis_user
--

CREATE TABLE public.vehicles (
    code character varying(50) NOT NULL,
    plate_number character varying(20) NOT NULL,
    vehicle_type public.vehicletype NOT NULL,
    uvis_device_id character varying(100),
    uvis_enabled boolean NOT NULL,
    max_pallets integer NOT NULL,
    max_weight_kg double precision NOT NULL,
    max_volume_cbm double precision,
    forklift_operator_available boolean NOT NULL,
    tonnage double precision NOT NULL,
    length_m double precision,
    width_m double precision,
    height_m double precision,
    driver_name character varying(100),
    driver_phone character varying(20),
    min_temp_celsius double precision,
    max_temp_celsius double precision,
    fuel_efficiency_km_per_liter double precision,
    fuel_cost_per_liter double precision,
    status public.vehiclestatus NOT NULL,
    garage_address character varying(500),
    garage_latitude double precision,
    garage_longitude double precision,
    notes text,
    is_active boolean NOT NULL,
    is_emergency boolean NOT NULL,
    emergency_type character varying(50),
    emergency_severity character varying(20),
    emergency_reported_at timestamp without time zone,
    emergency_location character varying(500),
    emergency_description text,
    estimated_repair_time integer,
    replacement_vehicle_id integer,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.vehicles OWNER TO uvis_user;

--
-- Name: COLUMN vehicles.code; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.code IS '차량코드';


--
-- Name: COLUMN vehicles.plate_number; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.plate_number IS '차량번호';


--
-- Name: COLUMN vehicles.vehicle_type; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.vehicle_type IS '온도대 구분';


--
-- Name: COLUMN vehicles.uvis_device_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.uvis_device_id IS 'UVIS 단말기 ID';


--
-- Name: COLUMN vehicles.uvis_enabled; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.uvis_enabled IS 'UVIS 연동 여부';


--
-- Name: COLUMN vehicles.max_pallets; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.max_pallets IS '최대 팔레트 수';


--
-- Name: COLUMN vehicles.max_weight_kg; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.max_weight_kg IS '최대 적재중량(kg)';


--
-- Name: COLUMN vehicles.max_volume_cbm; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.max_volume_cbm IS '최대 용적(CBM)';


--
-- Name: COLUMN vehicles.forklift_operator_available; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.forklift_operator_available IS '지게차 운전능력 가능 여부';


--
-- Name: COLUMN vehicles.tonnage; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.tonnage IS '톤수';


--
-- Name: COLUMN vehicles.length_m; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.length_m IS '적재함 길이(m)';


--
-- Name: COLUMN vehicles.width_m; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.width_m IS '적재함 너비(m)';


--
-- Name: COLUMN vehicles.height_m; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.height_m IS '적재함 높이(m)';


--
-- Name: COLUMN vehicles.driver_name; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.driver_name IS '운전자명';


--
-- Name: COLUMN vehicles.driver_phone; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.driver_phone IS '운전자 연락처';


--
-- Name: COLUMN vehicles.min_temp_celsius; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.min_temp_celsius IS '최저 온도(°C)';


--
-- Name: COLUMN vehicles.max_temp_celsius; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.max_temp_celsius IS '최고 온도(°C)';


--
-- Name: COLUMN vehicles.fuel_efficiency_km_per_liter; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.fuel_efficiency_km_per_liter IS '연비(km/L)';


--
-- Name: COLUMN vehicles.fuel_cost_per_liter; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.fuel_cost_per_liter IS '리터당 연료비';


--
-- Name: COLUMN vehicles.status; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.status IS '차량 상태';


--
-- Name: COLUMN vehicles.garage_address; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.garage_address IS '차고지 주소';


--
-- Name: COLUMN vehicles.garage_latitude; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.garage_latitude IS '차고지 위도';


--
-- Name: COLUMN vehicles.garage_longitude; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.garage_longitude IS '차고지 경도';


--
-- Name: COLUMN vehicles.notes; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.notes IS '특이사항';


--
-- Name: COLUMN vehicles.is_active; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.is_active IS '사용 여부';


--
-- Name: COLUMN vehicles.is_emergency; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.is_emergency IS '긴급 상황 여부';


--
-- Name: COLUMN vehicles.emergency_type; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.emergency_type IS '긴급 유형';


--
-- Name: COLUMN vehicles.emergency_severity; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.emergency_severity IS '긴급도';


--
-- Name: COLUMN vehicles.emergency_reported_at; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.emergency_reported_at IS '신고 시각';


--
-- Name: COLUMN vehicles.emergency_location; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.emergency_location IS '발생 위치';


--
-- Name: COLUMN vehicles.emergency_description; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.emergency_description IS '상황 설명';


--
-- Name: COLUMN vehicles.estimated_repair_time; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.estimated_repair_time IS '예상 수리 시간(분)';


--
-- Name: COLUMN vehicles.replacement_vehicle_id; Type: COMMENT; Schema: public; Owner: uvis_user
--

COMMENT ON COLUMN public.vehicles.replacement_vehicle_id IS '대체 차량 ID';


--
-- Name: vehicles_id_seq; Type: SEQUENCE; Schema: public; Owner: uvis_user
--

CREATE SEQUENCE public.vehicles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vehicles_id_seq OWNER TO uvis_user;

--
-- Name: vehicles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uvis_user
--

ALTER SEQUENCE public.vehicles_id_seq OWNED BY public.vehicles.id;


--
-- Name: ai_chat_histories id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.ai_chat_histories ALTER COLUMN id SET DEFAULT nextval('public.ai_chat_histories_id_seq'::regclass);


--
-- Name: ai_usage_logs id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.ai_usage_logs ALTER COLUMN id SET DEFAULT nextval('public.ai_usage_logs_id_seq'::regclass);


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: band_chat_rooms id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.band_chat_rooms ALTER COLUMN id SET DEFAULT nextval('public.band_chat_rooms_id_seq'::regclass);


--
-- Name: band_message_schedules id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.band_message_schedules ALTER COLUMN id SET DEFAULT nextval('public.band_message_schedules_id_seq'::regclass);


--
-- Name: band_messages id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.band_messages ALTER COLUMN id SET DEFAULT nextval('public.band_messages_id_seq'::regclass);


--
-- Name: billing_policies id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.billing_policies ALTER COLUMN id SET DEFAULT nextval('public.billing_policies_id_seq'::regclass);


--
-- Name: clients id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.clients ALTER COLUMN id SET DEFAULT nextval('public.clients_id_seq'::regclass);


--
-- Name: dispatch_routes id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.dispatch_routes ALTER COLUMN id SET DEFAULT nextval('public.dispatch_routes_id_seq'::regclass);


--
-- Name: dispatches id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.dispatches ALTER COLUMN id SET DEFAULT nextval('public.dispatches_id_seq'::regclass);


--
-- Name: driver_schedules id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.driver_schedules ALTER COLUMN id SET DEFAULT nextval('public.driver_schedules_id_seq'::regclass);


--
-- Name: driver_settlement_items id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.driver_settlement_items ALTER COLUMN id SET DEFAULT nextval('public.driver_settlement_items_id_seq'::regclass);


--
-- Name: driver_settlements id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.driver_settlements ALTER COLUMN id SET DEFAULT nextval('public.driver_settlements_id_seq'::regclass);


--
-- Name: drivers id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.drivers ALTER COLUMN id SET DEFAULT nextval('public.drivers_id_seq'::regclass);


--
-- Name: fcm_tokens id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.fcm_tokens ALTER COLUMN id SET DEFAULT nextval('public.fcm_tokens_id_seq'::regclass);


--
-- Name: invoice_line_items id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.invoice_line_items ALTER COLUMN id SET DEFAULT nextval('public.invoice_line_items_id_seq'::regclass);


--
-- Name: invoices id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.invoices ALTER COLUMN id SET DEFAULT nextval('public.invoices_id_seq'::regclass);


--
-- Name: maintenance_part_usage id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.maintenance_part_usage ALTER COLUMN id SET DEFAULT nextval('public.maintenance_part_usage_id_seq'::regclass);


--
-- Name: maintenance_schedules id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.maintenance_schedules ALTER COLUMN id SET DEFAULT nextval('public.maintenance_schedules_id_seq'::regclass);


--
-- Name: notices id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.notices ALTER COLUMN id SET DEFAULT nextval('public.notices_id_seq'::regclass);


--
-- Name: notification_templates id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.notification_templates ALTER COLUMN id SET DEFAULT nextval('public.notification_templates_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- Name: order_templates id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.order_templates ALTER COLUMN id SET DEFAULT nextval('public.order_templates_id_seq'::regclass);


--
-- Name: orders id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.orders ALTER COLUMN id SET DEFAULT nextval('public.orders_id_seq'::regclass);


--
-- Name: payments id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.payments ALTER COLUMN id SET DEFAULT nextval('public.payments_id_seq'::regclass);


--
-- Name: purchase_orders id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.purchase_orders ALTER COLUMN id SET DEFAULT nextval('public.purchase_orders_id_seq'::regclass);


--
-- Name: push_notification_logs id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.push_notification_logs ALTER COLUMN id SET DEFAULT nextval('public.push_notification_logs_id_seq'::regclass);


--
-- Name: recurring_orders id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.recurring_orders ALTER COLUMN id SET DEFAULT nextval('public.recurring_orders_id_seq'::regclass);


--
-- Name: security_alerts id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.security_alerts ALTER COLUMN id SET DEFAULT nextval('public.security_alerts_id_seq'::regclass);


--
-- Name: temperature_alerts id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.temperature_alerts ALTER COLUMN id SET DEFAULT nextval('public.temperature_alerts_id_seq'::regclass);


--
-- Name: two_factor_auth id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.two_factor_auth ALTER COLUMN id SET DEFAULT nextval('public.two_factor_auth_id_seq'::regclass);


--
-- Name: two_factor_logs id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.two_factor_logs ALTER COLUMN id SET DEFAULT nextval('public.two_factor_logs_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: uvis_access_keys id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.uvis_access_keys ALTER COLUMN id SET DEFAULT nextval('public.uvis_access_keys_id_seq'::regclass);


--
-- Name: uvis_api_logs id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.uvis_api_logs ALTER COLUMN id SET DEFAULT nextval('public.uvis_api_logs_id_seq'::regclass);


--
-- Name: vehicle_gps_logs id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicle_gps_logs ALTER COLUMN id SET DEFAULT nextval('public.vehicle_gps_logs_id_seq'::regclass);


--
-- Name: vehicle_inspections id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicle_inspections ALTER COLUMN id SET DEFAULT nextval('public.vehicle_inspections_id_seq'::regclass);


--
-- Name: vehicle_locations id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicle_locations ALTER COLUMN id SET DEFAULT nextval('public.vehicle_locations_id_seq'::regclass);


--
-- Name: vehicle_maintenance_records id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicle_maintenance_records ALTER COLUMN id SET DEFAULT nextval('public.vehicle_maintenance_records_id_seq'::regclass);


--
-- Name: vehicle_parts id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicle_parts ALTER COLUMN id SET DEFAULT nextval('public.vehicle_parts_id_seq'::regclass);


--
-- Name: vehicle_temperature_logs id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicle_temperature_logs ALTER COLUMN id SET DEFAULT nextval('public.vehicle_temperature_logs_id_seq'::regclass);


--
-- Name: vehicles id; Type: DEFAULT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicles ALTER COLUMN id SET DEFAULT nextval('public.vehicles_id_seq'::regclass);


--
-- Name: ai_chat_histories ai_chat_histories_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.ai_chat_histories
    ADD CONSTRAINT ai_chat_histories_pkey PRIMARY KEY (id);


--
-- Name: ai_usage_logs ai_usage_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.ai_usage_logs
    ADD CONSTRAINT ai_usage_logs_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: band_chat_rooms band_chat_rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.band_chat_rooms
    ADD CONSTRAINT band_chat_rooms_pkey PRIMARY KEY (id);


--
-- Name: band_message_schedules band_message_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.band_message_schedules
    ADD CONSTRAINT band_message_schedules_pkey PRIMARY KEY (id);


--
-- Name: band_messages band_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.band_messages
    ADD CONSTRAINT band_messages_pkey PRIMARY KEY (id);


--
-- Name: billing_policies billing_policies_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.billing_policies
    ADD CONSTRAINT billing_policies_pkey PRIMARY KEY (id);


--
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (id);


--
-- Name: dispatch_routes dispatch_routes_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.dispatch_routes
    ADD CONSTRAINT dispatch_routes_pkey PRIMARY KEY (id);


--
-- Name: dispatches dispatches_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.dispatches
    ADD CONSTRAINT dispatches_pkey PRIMARY KEY (id);


--
-- Name: driver_schedules driver_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.driver_schedules
    ADD CONSTRAINT driver_schedules_pkey PRIMARY KEY (id);


--
-- Name: driver_settlement_items driver_settlement_items_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.driver_settlement_items
    ADD CONSTRAINT driver_settlement_items_pkey PRIMARY KEY (id);


--
-- Name: driver_settlements driver_settlements_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.driver_settlements
    ADD CONSTRAINT driver_settlements_pkey PRIMARY KEY (id);


--
-- Name: drivers drivers_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.drivers
    ADD CONSTRAINT drivers_pkey PRIMARY KEY (id);


--
-- Name: fcm_tokens fcm_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.fcm_tokens
    ADD CONSTRAINT fcm_tokens_pkey PRIMARY KEY (id);


--
-- Name: invoice_line_items invoice_line_items_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.invoice_line_items
    ADD CONSTRAINT invoice_line_items_pkey PRIMARY KEY (id);


--
-- Name: invoices invoices_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_pkey PRIMARY KEY (id);


--
-- Name: maintenance_part_usage maintenance_part_usage_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.maintenance_part_usage
    ADD CONSTRAINT maintenance_part_usage_pkey PRIMARY KEY (id);


--
-- Name: maintenance_schedules maintenance_schedules_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.maintenance_schedules
    ADD CONSTRAINT maintenance_schedules_pkey PRIMARY KEY (id);


--
-- Name: notices notices_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.notices
    ADD CONSTRAINT notices_pkey PRIMARY KEY (id);


--
-- Name: notification_templates notification_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.notification_templates
    ADD CONSTRAINT notification_templates_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: order_templates order_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.order_templates
    ADD CONSTRAINT order_templates_pkey PRIMARY KEY (id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- Name: purchase_orders purchase_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.purchase_orders
    ADD CONSTRAINT purchase_orders_pkey PRIMARY KEY (id);


--
-- Name: push_notification_logs push_notification_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.push_notification_logs
    ADD CONSTRAINT push_notification_logs_pkey PRIMARY KEY (id);


--
-- Name: recurring_orders recurring_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.recurring_orders
    ADD CONSTRAINT recurring_orders_pkey PRIMARY KEY (id);


--
-- Name: security_alerts security_alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.security_alerts
    ADD CONSTRAINT security_alerts_pkey PRIMARY KEY (id);


--
-- Name: temperature_alerts temperature_alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.temperature_alerts
    ADD CONSTRAINT temperature_alerts_pkey PRIMARY KEY (id);


--
-- Name: two_factor_auth two_factor_auth_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.two_factor_auth
    ADD CONSTRAINT two_factor_auth_pkey PRIMARY KEY (id);


--
-- Name: two_factor_auth two_factor_auth_user_id_key; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.two_factor_auth
    ADD CONSTRAINT two_factor_auth_user_id_key UNIQUE (user_id);


--
-- Name: two_factor_logs two_factor_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.two_factor_logs
    ADD CONSTRAINT two_factor_logs_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: uvis_access_keys uvis_access_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.uvis_access_keys
    ADD CONSTRAINT uvis_access_keys_pkey PRIMARY KEY (id);


--
-- Name: uvis_api_logs uvis_api_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.uvis_api_logs
    ADD CONSTRAINT uvis_api_logs_pkey PRIMARY KEY (id);


--
-- Name: vehicle_gps_logs vehicle_gps_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicle_gps_logs
    ADD CONSTRAINT vehicle_gps_logs_pkey PRIMARY KEY (id);


--
-- Name: vehicle_inspections vehicle_inspections_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicle_inspections
    ADD CONSTRAINT vehicle_inspections_pkey PRIMARY KEY (id);


--
-- Name: vehicle_locations vehicle_locations_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicle_locations
    ADD CONSTRAINT vehicle_locations_pkey PRIMARY KEY (id);


--
-- Name: vehicle_maintenance_records vehicle_maintenance_records_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicle_maintenance_records
    ADD CONSTRAINT vehicle_maintenance_records_pkey PRIMARY KEY (id);


--
-- Name: vehicle_parts vehicle_parts_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicle_parts
    ADD CONSTRAINT vehicle_parts_pkey PRIMARY KEY (id);


--
-- Name: vehicle_temperature_logs vehicle_temperature_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicle_temperature_logs
    ADD CONSTRAINT vehicle_temperature_logs_pkey PRIMARY KEY (id);


--
-- Name: vehicles vehicles_pkey; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_pkey PRIMARY KEY (id);


--
-- Name: vehicles vehicles_plate_number_key; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_plate_number_key UNIQUE (plate_number);


--
-- Name: vehicles vehicles_uvis_device_id_key; Type: CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_uvis_device_id_key UNIQUE (uvis_device_id);


--
-- Name: idx_uvis_access_key_active; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX idx_uvis_access_key_active ON public.uvis_access_keys USING btree (is_active);


--
-- Name: idx_uvis_access_key_expires; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX idx_uvis_access_key_expires ON public.uvis_access_keys USING btree (expires_at);


--
-- Name: idx_uvis_log_created; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX idx_uvis_log_created ON public.uvis_api_logs USING btree (created_at);


--
-- Name: idx_uvis_log_type; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX idx_uvis_log_type ON public.uvis_api_logs USING btree (api_type);


--
-- Name: idx_vehicle_gps_created; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX idx_vehicle_gps_created ON public.vehicle_gps_logs USING btree (created_at);


--
-- Name: idx_vehicle_gps_date_time; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX idx_vehicle_gps_date_time ON public.vehicle_gps_logs USING btree (bi_date, bi_time);


--
-- Name: idx_vehicle_gps_tid; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX idx_vehicle_gps_tid ON public.vehicle_gps_logs USING btree (tid_id);


--
-- Name: idx_vehicle_gps_vehicle_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX idx_vehicle_gps_vehicle_id ON public.vehicle_gps_logs USING btree (vehicle_id);


--
-- Name: idx_vehicle_temp_created; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX idx_vehicle_temp_created ON public.vehicle_temperature_logs USING btree (created_at);


--
-- Name: idx_vehicle_temp_date_time; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX idx_vehicle_temp_date_time ON public.vehicle_temperature_logs USING btree (tpl_date, tpl_time);


--
-- Name: idx_vehicle_temp_tid; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX idx_vehicle_temp_tid ON public.vehicle_temperature_logs USING btree (tid_id);


--
-- Name: idx_vehicle_temp_vehicle_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX idx_vehicle_temp_vehicle_id ON public.vehicle_temperature_logs USING btree (vehicle_id);


--
-- Name: ix_ai_chat_histories_created_at; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_ai_chat_histories_created_at ON public.ai_chat_histories USING btree (created_at);


--
-- Name: ix_ai_chat_histories_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_ai_chat_histories_id ON public.ai_chat_histories USING btree (id);


--
-- Name: ix_ai_chat_histories_intent; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_ai_chat_histories_intent ON public.ai_chat_histories USING btree (intent);


--
-- Name: ix_ai_chat_histories_session_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_ai_chat_histories_session_id ON public.ai_chat_histories USING btree (session_id);


--
-- Name: ix_ai_chat_histories_user_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_ai_chat_histories_user_id ON public.ai_chat_histories USING btree (user_id);


--
-- Name: ix_ai_usage_logs_created_at; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_ai_usage_logs_created_at ON public.ai_usage_logs USING btree (created_at);


--
-- Name: ix_ai_usage_logs_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_ai_usage_logs_id ON public.ai_usage_logs USING btree (id);


--
-- Name: ix_ai_usage_logs_intent; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_ai_usage_logs_intent ON public.ai_usage_logs USING btree (intent);


--
-- Name: ix_ai_usage_logs_model_name; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_ai_usage_logs_model_name ON public.ai_usage_logs USING btree (model_name);


--
-- Name: ix_ai_usage_logs_provider; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_ai_usage_logs_provider ON public.ai_usage_logs USING btree (provider);


--
-- Name: ix_ai_usage_logs_session_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_ai_usage_logs_session_id ON public.ai_usage_logs USING btree (session_id);


--
-- Name: ix_ai_usage_logs_user_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_ai_usage_logs_user_id ON public.ai_usage_logs USING btree (user_id);


--
-- Name: ix_audit_logs_created_at; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_audit_logs_created_at ON public.audit_logs USING btree (created_at);


--
-- Name: ix_audit_logs_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_audit_logs_id ON public.audit_logs USING btree (id);


--
-- Name: ix_band_chat_rooms_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_band_chat_rooms_id ON public.band_chat_rooms USING btree (id);


--
-- Name: ix_band_message_schedules_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_band_message_schedules_id ON public.band_message_schedules USING btree (id);


--
-- Name: ix_band_messages_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_band_messages_id ON public.band_messages USING btree (id);


--
-- Name: ix_billing_policies_client_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_billing_policies_client_id ON public.billing_policies USING btree (client_id);


--
-- Name: ix_billing_policies_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_billing_policies_id ON public.billing_policies USING btree (id);


--
-- Name: ix_clients_code; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE UNIQUE INDEX ix_clients_code ON public.clients USING btree (code);


--
-- Name: ix_dispatches_dispatch_date; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_dispatches_dispatch_date ON public.dispatches USING btree (dispatch_date);


--
-- Name: ix_dispatches_dispatch_number; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE UNIQUE INDEX ix_dispatches_dispatch_number ON public.dispatches USING btree (dispatch_number);


--
-- Name: ix_dispatches_is_scheduled; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_dispatches_is_scheduled ON public.dispatches USING btree (is_scheduled);


--
-- Name: ix_dispatches_is_urgent; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_dispatches_is_urgent ON public.dispatches USING btree (is_urgent);


--
-- Name: ix_dispatches_scheduled_for_date; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_dispatches_scheduled_for_date ON public.dispatches USING btree (scheduled_for_date);


--
-- Name: ix_driver_schedules_driver_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_driver_schedules_driver_id ON public.driver_schedules USING btree (driver_id);


--
-- Name: ix_driver_schedules_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_driver_schedules_id ON public.driver_schedules USING btree (id);


--
-- Name: ix_driver_schedules_is_available; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_driver_schedules_is_available ON public.driver_schedules USING btree (is_available);


--
-- Name: ix_driver_schedules_schedule_date; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_driver_schedules_schedule_date ON public.driver_schedules USING btree (schedule_date);


--
-- Name: ix_driver_settlement_items_dispatch_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_driver_settlement_items_dispatch_id ON public.driver_settlement_items USING btree (dispatch_id);


--
-- Name: ix_driver_settlement_items_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_driver_settlement_items_id ON public.driver_settlement_items USING btree (id);


--
-- Name: ix_driver_settlement_items_settlement_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_driver_settlement_items_settlement_id ON public.driver_settlement_items USING btree (settlement_id);


--
-- Name: ix_driver_settlements_driver_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_driver_settlements_driver_id ON public.driver_settlements USING btree (driver_id);


--
-- Name: ix_driver_settlements_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_driver_settlements_id ON public.driver_settlements USING btree (id);


--
-- Name: ix_driver_settlements_settlement_number; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE UNIQUE INDEX ix_driver_settlements_settlement_number ON public.driver_settlements USING btree (settlement_number);


--
-- Name: ix_drivers_code; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE UNIQUE INDEX ix_drivers_code ON public.drivers USING btree (code);


--
-- Name: ix_fcm_tokens_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_fcm_tokens_id ON public.fcm_tokens USING btree (id);


--
-- Name: ix_fcm_tokens_token; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE UNIQUE INDEX ix_fcm_tokens_token ON public.fcm_tokens USING btree (token);


--
-- Name: ix_invoice_line_items_dispatch_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_invoice_line_items_dispatch_id ON public.invoice_line_items USING btree (dispatch_id);


--
-- Name: ix_invoice_line_items_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_invoice_line_items_id ON public.invoice_line_items USING btree (id);


--
-- Name: ix_invoice_line_items_invoice_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_invoice_line_items_invoice_id ON public.invoice_line_items USING btree (invoice_id);


--
-- Name: ix_invoices_client_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_invoices_client_id ON public.invoices USING btree (client_id);


--
-- Name: ix_invoices_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_invoices_id ON public.invoices USING btree (id);


--
-- Name: ix_invoices_invoice_number; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE UNIQUE INDEX ix_invoices_invoice_number ON public.invoices USING btree (invoice_number);


--
-- Name: ix_invoices_status; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_invoices_status ON public.invoices USING btree (status);


--
-- Name: ix_maintenance_part_usage_maintenance_record_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_maintenance_part_usage_maintenance_record_id ON public.maintenance_part_usage USING btree (maintenance_record_id);


--
-- Name: ix_maintenance_part_usage_part_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_maintenance_part_usage_part_id ON public.maintenance_part_usage USING btree (part_id);


--
-- Name: ix_maintenance_schedules_next_maintenance_date; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_maintenance_schedules_next_maintenance_date ON public.maintenance_schedules USING btree (next_maintenance_date);


--
-- Name: ix_maintenance_schedules_vehicle_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_maintenance_schedules_vehicle_id ON public.maintenance_schedules USING btree (vehicle_id);


--
-- Name: ix_notices_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_notices_id ON public.notices USING btree (id);


--
-- Name: ix_notification_templates_channel; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_notification_templates_channel ON public.notification_templates USING btree (channel);


--
-- Name: ix_notification_templates_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_notification_templates_id ON public.notification_templates USING btree (id);


--
-- Name: ix_notification_templates_notification_type; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_notification_templates_notification_type ON public.notification_templates USING btree (notification_type);


--
-- Name: ix_notification_templates_template_code; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE UNIQUE INDEX ix_notification_templates_template_code ON public.notification_templates USING btree (template_code);


--
-- Name: ix_notifications_channel; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_notifications_channel ON public.notifications USING btree (channel);


--
-- Name: ix_notifications_dispatch_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_notifications_dispatch_id ON public.notifications USING btree (dispatch_id);


--
-- Name: ix_notifications_driver_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_notifications_driver_id ON public.notifications USING btree (driver_id);


--
-- Name: ix_notifications_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_notifications_id ON public.notifications USING btree (id);


--
-- Name: ix_notifications_notification_type; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_notifications_notification_type ON public.notifications USING btree (notification_type);


--
-- Name: ix_notifications_order_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_notifications_order_id ON public.notifications USING btree (order_id);


--
-- Name: ix_notifications_recipient_email; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_notifications_recipient_email ON public.notifications USING btree (recipient_email);


--
-- Name: ix_notifications_recipient_phone; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_notifications_recipient_phone ON public.notifications USING btree (recipient_phone);


--
-- Name: ix_notifications_status; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_notifications_status ON public.notifications USING btree (status);


--
-- Name: ix_notifications_vehicle_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_notifications_vehicle_id ON public.notifications USING btree (vehicle_id);


--
-- Name: ix_order_templates_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_order_templates_id ON public.order_templates USING btree (id);


--
-- Name: ix_order_templates_is_active; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_order_templates_is_active ON public.order_templates USING btree (is_active);


--
-- Name: ix_order_templates_name; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_order_templates_name ON public.order_templates USING btree (name);


--
-- Name: ix_orders_order_number; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE UNIQUE INDEX ix_orders_order_number ON public.orders USING btree (order_number);


--
-- Name: ix_payments_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_payments_id ON public.payments USING btree (id);


--
-- Name: ix_payments_invoice_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_payments_invoice_id ON public.payments USING btree (invoice_id);


--
-- Name: ix_payments_payment_number; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE UNIQUE INDEX ix_payments_payment_number ON public.payments USING btree (payment_number);


--
-- Name: ix_purchase_orders_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_purchase_orders_id ON public.purchase_orders USING btree (id);


--
-- Name: ix_push_notification_logs_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_push_notification_logs_id ON public.push_notification_logs USING btree (id);


--
-- Name: ix_recurring_orders_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_recurring_orders_id ON public.recurring_orders USING btree (id);


--
-- Name: ix_security_alerts_created_at; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_security_alerts_created_at ON public.security_alerts USING btree (created_at);


--
-- Name: ix_security_alerts_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_security_alerts_id ON public.security_alerts USING btree (id);


--
-- Name: ix_temperature_alerts_detected_at; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_temperature_alerts_detected_at ON public.temperature_alerts USING btree (detected_at);


--
-- Name: ix_temperature_alerts_dispatch_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_temperature_alerts_dispatch_id ON public.temperature_alerts USING btree (dispatch_id);


--
-- Name: ix_temperature_alerts_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_temperature_alerts_id ON public.temperature_alerts USING btree (id);


--
-- Name: ix_temperature_alerts_is_resolved; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_temperature_alerts_is_resolved ON public.temperature_alerts USING btree (is_resolved);


--
-- Name: ix_temperature_alerts_vehicle_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_temperature_alerts_vehicle_id ON public.temperature_alerts USING btree (vehicle_id);


--
-- Name: ix_two_factor_auth_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_two_factor_auth_id ON public.two_factor_auth USING btree (id);


--
-- Name: ix_two_factor_logs_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_two_factor_logs_id ON public.two_factor_logs USING btree (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: ix_uvis_access_keys_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_uvis_access_keys_id ON public.uvis_access_keys USING btree (id);


--
-- Name: ix_uvis_api_logs_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_uvis_api_logs_id ON public.uvis_api_logs USING btree (id);


--
-- Name: ix_vehicle_gps_logs_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_vehicle_gps_logs_id ON public.vehicle_gps_logs USING btree (id);


--
-- Name: ix_vehicle_gps_logs_tid_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_vehicle_gps_logs_tid_id ON public.vehicle_gps_logs USING btree (tid_id);


--
-- Name: ix_vehicle_inspections_expiry_date; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_vehicle_inspections_expiry_date ON public.vehicle_inspections USING btree (expiry_date);


--
-- Name: ix_vehicle_inspections_vehicle_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_vehicle_inspections_vehicle_id ON public.vehicle_inspections USING btree (vehicle_id);


--
-- Name: ix_vehicle_locations_dispatch_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_vehicle_locations_dispatch_id ON public.vehicle_locations USING btree (dispatch_id);


--
-- Name: ix_vehicle_locations_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_vehicle_locations_id ON public.vehicle_locations USING btree (id);


--
-- Name: ix_vehicle_locations_recorded_at; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_vehicle_locations_recorded_at ON public.vehicle_locations USING btree (recorded_at);


--
-- Name: ix_vehicle_locations_vehicle_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_vehicle_locations_vehicle_id ON public.vehicle_locations USING btree (vehicle_id);


--
-- Name: ix_vehicle_maintenance_records_maintenance_number; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE UNIQUE INDEX ix_vehicle_maintenance_records_maintenance_number ON public.vehicle_maintenance_records USING btree (maintenance_number);


--
-- Name: ix_vehicle_maintenance_records_scheduled_date; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_vehicle_maintenance_records_scheduled_date ON public.vehicle_maintenance_records USING btree (scheduled_date);


--
-- Name: ix_vehicle_maintenance_records_vehicle_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_vehicle_maintenance_records_vehicle_id ON public.vehicle_maintenance_records USING btree (vehicle_id);


--
-- Name: ix_vehicle_parts_part_number; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE UNIQUE INDEX ix_vehicle_parts_part_number ON public.vehicle_parts USING btree (part_number);


--
-- Name: ix_vehicle_temperature_logs_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_vehicle_temperature_logs_id ON public.vehicle_temperature_logs USING btree (id);


--
-- Name: ix_vehicle_temperature_logs_tid_id; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE INDEX ix_vehicle_temperature_logs_tid_id ON public.vehicle_temperature_logs USING btree (tid_id);


--
-- Name: ix_vehicles_code; Type: INDEX; Schema: public; Owner: uvis_user
--

CREATE UNIQUE INDEX ix_vehicles_code ON public.vehicles USING btree (code);


--
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: band_message_schedules band_message_schedules_dispatch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.band_message_schedules
    ADD CONSTRAINT band_message_schedules_dispatch_id_fkey FOREIGN KEY (dispatch_id) REFERENCES public.dispatches(id);


--
-- Name: band_messages band_messages_dispatch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.band_messages
    ADD CONSTRAINT band_messages_dispatch_id_fkey FOREIGN KEY (dispatch_id) REFERENCES public.dispatches(id);


--
-- Name: billing_policies billing_policies_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.billing_policies
    ADD CONSTRAINT billing_policies_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- Name: dispatch_routes dispatch_routes_dispatch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.dispatch_routes
    ADD CONSTRAINT dispatch_routes_dispatch_id_fkey FOREIGN KEY (dispatch_id) REFERENCES public.dispatches(id);


--
-- Name: dispatch_routes dispatch_routes_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.dispatch_routes
    ADD CONSTRAINT dispatch_routes_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id);


--
-- Name: dispatches dispatches_driver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.dispatches
    ADD CONSTRAINT dispatches_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.drivers(id);


--
-- Name: dispatches dispatches_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.dispatches
    ADD CONSTRAINT dispatches_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: driver_schedules driver_schedules_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.driver_schedules
    ADD CONSTRAINT driver_schedules_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: driver_schedules driver_schedules_driver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.driver_schedules
    ADD CONSTRAINT driver_schedules_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.drivers(id);


--
-- Name: driver_settlement_items driver_settlement_items_dispatch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.driver_settlement_items
    ADD CONSTRAINT driver_settlement_items_dispatch_id_fkey FOREIGN KEY (dispatch_id) REFERENCES public.dispatches(id);


--
-- Name: driver_settlement_items driver_settlement_items_settlement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.driver_settlement_items
    ADD CONSTRAINT driver_settlement_items_settlement_id_fkey FOREIGN KEY (settlement_id) REFERENCES public.driver_settlements(id);


--
-- Name: driver_settlements driver_settlements_driver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.driver_settlements
    ADD CONSTRAINT driver_settlements_driver_id_fkey FOREIGN KEY (driver_id) REFERENCES public.drivers(id);


--
-- Name: fcm_tokens fcm_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.fcm_tokens
    ADD CONSTRAINT fcm_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: invoice_line_items invoice_line_items_dispatch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.invoice_line_items
    ADD CONSTRAINT invoice_line_items_dispatch_id_fkey FOREIGN KEY (dispatch_id) REFERENCES public.dispatches(id);


--
-- Name: invoice_line_items invoice_line_items_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.invoice_line_items
    ADD CONSTRAINT invoice_line_items_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id);


--
-- Name: invoices invoices_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- Name: invoices invoices_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: maintenance_part_usage maintenance_part_usage_maintenance_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.maintenance_part_usage
    ADD CONSTRAINT maintenance_part_usage_maintenance_record_id_fkey FOREIGN KEY (maintenance_record_id) REFERENCES public.vehicle_maintenance_records(id);


--
-- Name: maintenance_part_usage maintenance_part_usage_part_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.maintenance_part_usage
    ADD CONSTRAINT maintenance_part_usage_part_id_fkey FOREIGN KEY (part_id) REFERENCES public.vehicle_parts(id);


--
-- Name: maintenance_schedules maintenance_schedules_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.maintenance_schedules
    ADD CONSTRAINT maintenance_schedules_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: orders orders_delivery_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_delivery_client_id_fkey FOREIGN KEY (delivery_client_id) REFERENCES public.clients(id);


--
-- Name: orders orders_pickup_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pickup_client_id_fkey FOREIGN KEY (pickup_client_id) REFERENCES public.clients(id);


--
-- Name: payments payments_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: payments payments_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id);


--
-- Name: push_notification_logs push_notification_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.push_notification_logs
    ADD CONSTRAINT push_notification_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: security_alerts security_alerts_resolved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.security_alerts
    ADD CONSTRAINT security_alerts_resolved_by_fkey FOREIGN KEY (resolved_by) REFERENCES public.users(id);


--
-- Name: security_alerts security_alerts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.security_alerts
    ADD CONSTRAINT security_alerts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: temperature_alerts temperature_alerts_dispatch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.temperature_alerts
    ADD CONSTRAINT temperature_alerts_dispatch_id_fkey FOREIGN KEY (dispatch_id) REFERENCES public.dispatches(id);


--
-- Name: temperature_alerts temperature_alerts_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.temperature_alerts
    ADD CONSTRAINT temperature_alerts_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.vehicle_locations(id);


--
-- Name: temperature_alerts temperature_alerts_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.temperature_alerts
    ADD CONSTRAINT temperature_alerts_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: two_factor_auth two_factor_auth_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.two_factor_auth
    ADD CONSTRAINT two_factor_auth_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: two_factor_logs two_factor_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.two_factor_logs
    ADD CONSTRAINT two_factor_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: vehicle_gps_logs vehicle_gps_logs_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicle_gps_logs
    ADD CONSTRAINT vehicle_gps_logs_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: vehicle_inspections vehicle_inspections_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicle_inspections
    ADD CONSTRAINT vehicle_inspections_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: vehicle_locations vehicle_locations_dispatch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicle_locations
    ADD CONSTRAINT vehicle_locations_dispatch_id_fkey FOREIGN KEY (dispatch_id) REFERENCES public.dispatches(id);


--
-- Name: vehicle_locations vehicle_locations_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicle_locations
    ADD CONSTRAINT vehicle_locations_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: vehicle_maintenance_records vehicle_maintenance_records_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicle_maintenance_records
    ADD CONSTRAINT vehicle_maintenance_records_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: vehicle_temperature_logs vehicle_temperature_logs_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uvis_user
--

ALTER TABLE ONLY public.vehicle_temperature_logs
    ADD CONSTRAINT vehicle_temperature_logs_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- PostgreSQL database dump complete
--

\unrestrict 6NL0AqDvjEWX3nPVmLNQ61iDEeHywD56zJrevsoDR76NgZh4gJpbI7qnbK4bzBz

