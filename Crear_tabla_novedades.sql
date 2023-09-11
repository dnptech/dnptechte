--
-- PostgreSQL database dump
--

-- Dumped from database version 14.9 (Ubuntu 14.9-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.9 (Ubuntu 14.9-0ubuntu0.22.04.1)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: novedades; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.novedades (
    id integer NOT NULL,
    cuij character varying,
    titulo character varying,
    numero character varying,
    firmantes character varying,
	fecha_firma timestamp without time zone,
    adjuntos character varying,
    actuaciones character varying,
    fecha_diligenciamiento timestamp without time zone,
    created timestamp without time zone DEFAULT now()
);


ALTER TABLE public.novedades OWNER TO postgres;

--
-- Name: novedades_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.novedades_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.novedades_id_seq OWNER TO postgres;

--
-- Name: novedades_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.novedades_id_seq OWNED BY public.novedades.id;


--
-- Name: novedades id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.novedades ALTER COLUMN id SET DEFAULT nextval('public.novedades_id_seq'::regclass);


--
-- PostgreSQL database dump complete
--

