--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

-- Started on 2025-04-29 18:11:51

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 7 (class 2615 OID 24763)
-- Name: update-14 april; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA "update-14 april";


ALTER SCHEMA "update-14 april" OWNER TO postgres;

--
-- TOC entry 2 (class 3079 OID 17521)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- TOC entry 5221 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- TOC entry 257 (class 1255 OID 17799)
-- Name: update_modified_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_modified_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_modified_column() OWNER TO postgres;

--
-- TOC entry 258 (class 1255 OID 17834)
-- Name: user_has_permission(uuid, character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.user_has_permission(user_id uuid, permission_name character varying) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
DECLARE
    user_role VARCHAR;
BEGIN
    -- Get user role
    SELECT role INTO user_role FROM users WHERE id = user_id;
    
    -- Admin role has all permissions
    IF user_role = 'admin' THEN
        RETURN TRUE;
    END IF;
    
    -- Check specific permission
    RETURN EXISTS (
        SELECT 1 
        FROM user_permissions up
        JOIN admin_permissions ap ON up.permission_id = ap.id
        WHERE up.user_id = user_id AND ap.name = permission_name
    );
END;
$$;


ALTER FUNCTION public.user_has_permission(user_id uuid, permission_name character varying) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 238 (class 1259 OID 24581)
-- Name: additive_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.additive_categories (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    name_hindi character varying(100),
    name_gujarati character varying(100),
    name_marathi character varying(100),
    name_tamil character varying(100)
);


ALTER TABLE public.additive_categories OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 24589)
-- Name: additives; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.additives (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(255) NOT NULL,
    category_id uuid,
    description text,
    health_implications text,
    is_natural boolean DEFAULT false,
    is_vegan boolean DEFAULT true,
    is_verified boolean DEFAULT false,
    added_by_user_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.additives OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 17808)
-- Name: admin_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.admin_permissions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(50) NOT NULL,
    description text
);


ALTER TABLE public.admin_permissions OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 17630)
-- Name: base_ingredients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.base_ingredients (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(100) NOT NULL,
    name_hindi character varying(100),
    name_gujarati character varying(100),
    name_marathi character varying(100),
    name_tamil character varying(100),
    category_id uuid,
    added_by_user_id uuid,
    is_verified boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.base_ingredients OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 17650)
-- Name: branded_ingredients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.branded_ingredients (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    base_ingredient_id uuid NOT NULL,
    brand_id uuid NOT NULL,
    added_by_user_id uuid,
    image_url text,
    description text,
    is_verified boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.branded_ingredients OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 17617)
-- Name: brands; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.brands (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(100) NOT NULL,
    added_by_user_id uuid,
    is_verified boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.brands OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 17580)
-- Name: cuisines; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cuisines (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(100) NOT NULL,
    name_hindi character varying(100),
    name_gujarati character varying(100),
    name_marathi character varying(100),
    name_tamil character varying(100)
);


ALTER TABLE public.cuisines OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 17547)
-- Name: families; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.families (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(100) NOT NULL,
    created_by_user_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.families OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 17559)
-- Name: family_members; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.family_members (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    family_id uuid NOT NULL,
    user_id uuid,
    role character varying(20) DEFAULT 'member'::character varying NOT NULL,
    is_active boolean DEFAULT true,
    joined_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    relationship character varying(50),
    invitation_status character varying(20) DEFAULT 'pending'::character varying,
    invitation_token character varying(100),
    first_name character varying(100),
    last_name character varying(100),
    email character varying(255),
    phone character varying(20)
);


ALTER TABLE public.family_members OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 17609)
-- Name: ingredient_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ingredient_categories (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(100) NOT NULL,
    name_hindi character varying(100),
    name_gujarati character varying(100),
    name_marathi character varying(100),
    name_tamil character varying(100)
);


ALTER TABLE public.ingredient_categories OWNER TO postgres;

--
-- TOC entry 246 (class 1259 OID 24737)
-- Name: ingredient_lists; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ingredient_lists (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    branded_ingredient_id uuid NOT NULL,
    ingredients_text text NOT NULL,
    extracted_from_image uuid,
    is_verified boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.ingredient_lists OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 24654)
-- Name: nutrient_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nutrient_categories (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    display_order integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.nutrient_categories OWNER TO postgres;

--
-- TOC entry 242 (class 1259 OID 24663)
-- Name: nutrients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nutrients (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    category_id uuid,
    name character varying(100) NOT NULL,
    short_name character varying(20),
    unit character varying(20) NOT NULL,
    daily_value numeric(10,2),
    description text,
    display_order integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.nutrients OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 24716)
-- Name: product_additives; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product_additives (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    branded_ingredient_id uuid NOT NULL,
    additive_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.product_additives OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 24637)
-- Name: product_images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product_images (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    branded_ingredient_id uuid NOT NULL,
    image_url text NOT NULL,
    image_type character varying(50),
    is_primary boolean DEFAULT false,
    extracted_text text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.product_images OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 24680)
-- Name: product_nutrients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product_nutrients (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    branded_ingredient_id uuid NOT NULL,
    nutrient_id uuid NOT NULL,
    amount numeric(10,2) NOT NULL,
    percent_daily_value numeric(5,2),
    per_serving boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.product_nutrients OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 17683)
-- Name: recipe_ingredients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recipe_ingredients (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    recipe_id uuid NOT NULL,
    branded_ingredient_id uuid NOT NULL,
    quantity character varying(100),
    unit_id uuid,
    display_order integer DEFAULT 0 NOT NULL,
    notes text
);


ALTER TABLE public.recipe_ingredients OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 17720)
-- Name: recipe_media; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recipe_media (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    recipe_id uuid NOT NULL,
    media_url text NOT NULL,
    media_type character varying(10) NOT NULL,
    display_order integer DEFAULT 0
);


ALTER TABLE public.recipe_media OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 17758)
-- Name: recipe_sharing; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recipe_sharing (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    recipe_id uuid NOT NULL,
    family_id uuid NOT NULL,
    shared_by_user_id uuid NOT NULL,
    shared_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.recipe_sharing OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 17707)
-- Name: recipe_steps; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recipe_steps (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    recipe_id uuid NOT NULL,
    description text NOT NULL,
    step_number integer NOT NULL,
    media_url text,
    media_type character varying(10)
);


ALTER TABLE public.recipe_steps OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 17740)
-- Name: recipe_tags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recipe_tags (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    recipe_id uuid NOT NULL,
    tag_id uuid NOT NULL
);


ALTER TABLE public.recipe_tags OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 17588)
-- Name: recipes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recipes (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    created_by_user_id uuid NOT NULL,
    servings integer,
    prep_time_minutes integer,
    cook_time_minutes integer,
    cuisine_id uuid,
    is_private boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    image_url text
);


ALTER TABLE public.recipes OWNER TO postgres;

--
-- TOC entry 244 (class 1259 OID 24703)
-- Name: serving_info; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.serving_info (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    branded_ingredient_id uuid NOT NULL,
    serving_size numeric(10,2) NOT NULL,
    serving_unit character varying(50) NOT NULL,
    servings_per_container numeric(10,2)
);


ALTER TABLE public.serving_info OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 17734)
-- Name: tags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tags (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(50) NOT NULL,
    name_hindi character varying(50),
    name_gujarati character varying(50),
    name_marathi character varying(50),
    name_tamil character varying(50)
);


ALTER TABLE public.tags OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 17677)
-- Name: units; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.units (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(50) NOT NULL,
    short_name character varying(10) NOT NULL,
    name_hindi character varying(50),
    name_gujarati character varying(50),
    name_marathi character varying(50),
    name_tamil character varying(50),
    unit_type character varying(20) NOT NULL
);


ALTER TABLE public.units OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 17816)
-- Name: user_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_permissions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    permission_id uuid NOT NULL
);


ALTER TABLE public.user_permissions OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 17532)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    email character varying(255) NOT NULL,
    phone character varying(20),
    password_hash character varying(255) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    profile_pic_url text,
    preferred_language character varying(10) DEFAULT 'en'::character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    role character varying(20) DEFAULT 'user'::character varying
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 17802)
-- Name: v_branded_ingredients; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_branded_ingredients AS
 SELECT bi.id,
    bi.base_ingredient_id,
    bi.brand_id,
    bi.is_verified,
    bi.added_by_user_id,
    bi.created_at,
    b.name AS brand_name,
    i.name AS ingredient_name,
    i.category_id,
    concat(b.name, ' ', i.name) AS full_name
   FROM ((public.branded_ingredients bi
     JOIN public.base_ingredients i ON ((bi.base_ingredient_id = i.id)))
     JOIN public.brands b ON ((bi.brand_id = b.id)));


ALTER VIEW public.v_branded_ingredients OWNER TO postgres;

--
-- TOC entry 4994 (class 2606 OID 24588)
-- Name: additive_categories additive_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.additive_categories
    ADD CONSTRAINT additive_categories_pkey PRIMARY KEY (id);


--
-- TOC entry 4996 (class 2606 OID 24633)
-- Name: additives additives_code_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.additives
    ADD CONSTRAINT additives_code_unique UNIQUE (code);


--
-- TOC entry 4998 (class 2606 OID 24600)
-- Name: additives additives_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.additives
    ADD CONSTRAINT additives_pkey PRIMARY KEY (id);


--
-- TOC entry 4988 (class 2606 OID 17815)
-- Name: admin_permissions admin_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admin_permissions
    ADD CONSTRAINT admin_permissions_pkey PRIMARY KEY (id);


--
-- TOC entry 4952 (class 2606 OID 17639)
-- Name: base_ingredients base_ingredients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.base_ingredients
    ADD CONSTRAINT base_ingredients_pkey PRIMARY KEY (id);


--
-- TOC entry 4956 (class 2606 OID 17661)
-- Name: branded_ingredients branded_ingredients_base_ingredient_id_brand_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branded_ingredients
    ADD CONSTRAINT branded_ingredients_base_ingredient_id_brand_id_key UNIQUE (base_ingredient_id, brand_id);


--
-- TOC entry 4958 (class 2606 OID 17659)
-- Name: branded_ingredients branded_ingredients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branded_ingredients
    ADD CONSTRAINT branded_ingredients_pkey PRIMARY KEY (id);


--
-- TOC entry 4949 (class 2606 OID 17624)
-- Name: brands brands_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brands
    ADD CONSTRAINT brands_pkey PRIMARY KEY (id);


--
-- TOC entry 4941 (class 2606 OID 17587)
-- Name: cuisines cuisines_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cuisines
    ADD CONSTRAINT cuisines_pkey PRIMARY KEY (id);


--
-- TOC entry 4933 (class 2606 OID 17553)
-- Name: families families_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.families
    ADD CONSTRAINT families_pkey PRIMARY KEY (id);


--
-- TOC entry 4935 (class 2606 OID 17569)
-- Name: family_members family_members_family_id_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.family_members
    ADD CONSTRAINT family_members_family_id_user_id_key UNIQUE (family_id, user_id);


--
-- TOC entry 4937 (class 2606 OID 17567)
-- Name: family_members family_members_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.family_members
    ADD CONSTRAINT family_members_pkey PRIMARY KEY (id);


--
-- TOC entry 4947 (class 2606 OID 17616)
-- Name: ingredient_categories ingredient_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ingredient_categories
    ADD CONSTRAINT ingredient_categories_pkey PRIMARY KEY (id);


--
-- TOC entry 5029 (class 2606 OID 24749)
-- Name: ingredient_lists ingredient_lists_branded_ingredient_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ingredient_lists
    ADD CONSTRAINT ingredient_lists_branded_ingredient_id_key UNIQUE (branded_ingredient_id);


--
-- TOC entry 5031 (class 2606 OID 24747)
-- Name: ingredient_lists ingredient_lists_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ingredient_lists
    ADD CONSTRAINT ingredient_lists_pkey PRIMARY KEY (id);


--
-- TOC entry 5005 (class 2606 OID 24662)
-- Name: nutrient_categories nutrient_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nutrient_categories
    ADD CONSTRAINT nutrient_categories_pkey PRIMARY KEY (id);


--
-- TOC entry 5008 (class 2606 OID 24673)
-- Name: nutrients nutrients_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nutrients
    ADD CONSTRAINT nutrients_name_key UNIQUE (name);


--
-- TOC entry 5010 (class 2606 OID 24671)
-- Name: nutrients nutrients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nutrients
    ADD CONSTRAINT nutrients_pkey PRIMARY KEY (id);


--
-- TOC entry 5024 (class 2606 OID 24724)
-- Name: product_additives product_additives_branded_ingredient_id_additive_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_additives
    ADD CONSTRAINT product_additives_branded_ingredient_id_additive_id_key UNIQUE (branded_ingredient_id, additive_id);


--
-- TOC entry 5026 (class 2606 OID 24722)
-- Name: product_additives product_additives_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_additives
    ADD CONSTRAINT product_additives_pkey PRIMARY KEY (id);


--
-- TOC entry 5003 (class 2606 OID 24646)
-- Name: product_images product_images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_images
    ADD CONSTRAINT product_images_pkey PRIMARY KEY (id);


--
-- TOC entry 5014 (class 2606 OID 24690)
-- Name: product_nutrients product_nutrients_branded_ingredient_id_nutrient_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_nutrients
    ADD CONSTRAINT product_nutrients_branded_ingredient_id_nutrient_id_key UNIQUE (branded_ingredient_id, nutrient_id);


--
-- TOC entry 5016 (class 2606 OID 24688)
-- Name: product_nutrients product_nutrients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_nutrients
    ADD CONSTRAINT product_nutrients_pkey PRIMARY KEY (id);


--
-- TOC entry 4966 (class 2606 OID 17691)
-- Name: recipe_ingredients recipe_ingredients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipe_ingredients
    ADD CONSTRAINT recipe_ingredients_pkey PRIMARY KEY (id);


--
-- TOC entry 4972 (class 2606 OID 17728)
-- Name: recipe_media recipe_media_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipe_media
    ADD CONSTRAINT recipe_media_pkey PRIMARY KEY (id);


--
-- TOC entry 4984 (class 2606 OID 17764)
-- Name: recipe_sharing recipe_sharing_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipe_sharing
    ADD CONSTRAINT recipe_sharing_pkey PRIMARY KEY (id);


--
-- TOC entry 4986 (class 2606 OID 17766)
-- Name: recipe_sharing recipe_sharing_recipe_id_family_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipe_sharing
    ADD CONSTRAINT recipe_sharing_recipe_id_family_id_key UNIQUE (recipe_id, family_id);


--
-- TOC entry 4969 (class 2606 OID 17714)
-- Name: recipe_steps recipe_steps_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipe_steps
    ADD CONSTRAINT recipe_steps_pkey PRIMARY KEY (id);


--
-- TOC entry 4978 (class 2606 OID 17745)
-- Name: recipe_tags recipe_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipe_tags
    ADD CONSTRAINT recipe_tags_pkey PRIMARY KEY (id);


--
-- TOC entry 4980 (class 2606 OID 17747)
-- Name: recipe_tags recipe_tags_recipe_id_tag_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipe_tags
    ADD CONSTRAINT recipe_tags_recipe_id_tag_id_key UNIQUE (recipe_id, tag_id);


--
-- TOC entry 4945 (class 2606 OID 17598)
-- Name: recipes recipes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipes
    ADD CONSTRAINT recipes_pkey PRIMARY KEY (id);


--
-- TOC entry 5018 (class 2606 OID 24710)
-- Name: serving_info serving_info_branded_ingredient_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.serving_info
    ADD CONSTRAINT serving_info_branded_ingredient_id_key UNIQUE (branded_ingredient_id);


--
-- TOC entry 5020 (class 2606 OID 24708)
-- Name: serving_info serving_info_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.serving_info
    ADD CONSTRAINT serving_info_pkey PRIMARY KEY (id);


--
-- TOC entry 4974 (class 2606 OID 17739)
-- Name: tags tags_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (id);


--
-- TOC entry 4962 (class 2606 OID 17682)
-- Name: units units_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.units
    ADD CONSTRAINT units_pkey PRIMARY KEY (id);


--
-- TOC entry 4990 (class 2606 OID 17821)
-- Name: user_permissions user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT user_permissions_pkey PRIMARY KEY (id);


--
-- TOC entry 4992 (class 2606 OID 17823)
-- Name: user_permissions user_permissions_user_id_permission_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT user_permissions_user_id_permission_id_key UNIQUE (user_id, permission_id);


--
-- TOC entry 4927 (class 2606 OID 17544)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 4929 (class 2606 OID 17546)
-- Name: users users_phone_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_phone_key UNIQUE (phone);


--
-- TOC entry 4931 (class 2606 OID 17542)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4999 (class 1259 OID 24629)
-- Name: idx_additives_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_additives_category ON public.additives USING btree (category_id);


--
-- TOC entry 4953 (class 1259 OID 17796)
-- Name: idx_base_ingredients_category_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_base_ingredients_category_id ON public.base_ingredients USING btree (category_id);


--
-- TOC entry 4954 (class 1259 OID 17797)
-- Name: idx_base_ingredients_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_base_ingredients_name ON public.base_ingredients USING btree (name);


--
-- TOC entry 4959 (class 1259 OID 17784)
-- Name: idx_branded_ingredients_base_ingredient_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_branded_ingredients_base_ingredient_id ON public.branded_ingredients USING btree (base_ingredient_id);


--
-- TOC entry 4960 (class 1259 OID 17785)
-- Name: idx_branded_ingredients_brand_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_branded_ingredients_brand_id ON public.branded_ingredients USING btree (brand_id);


--
-- TOC entry 4950 (class 1259 OID 17798)
-- Name: idx_brands_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_brands_name ON public.brands USING btree (name);


--
-- TOC entry 4938 (class 1259 OID 17794)
-- Name: idx_family_members_family_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_family_members_family_id ON public.family_members USING btree (family_id);


--
-- TOC entry 4939 (class 1259 OID 17795)
-- Name: idx_family_members_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_family_members_user_id ON public.family_members USING btree (user_id);


--
-- TOC entry 5027 (class 1259 OID 24760)
-- Name: idx_ingredient_lists_branded_ingredient; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ingredient_lists_branded_ingredient ON public.ingredient_lists USING btree (branded_ingredient_id);


--
-- TOC entry 5006 (class 1259 OID 24679)
-- Name: idx_nutrients_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_nutrients_category ON public.nutrients USING btree (category_id);


--
-- TOC entry 5000 (class 1259 OID 24652)
-- Name: idx_one_primary_image_per_product; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_one_primary_image_per_product ON public.product_images USING btree (branded_ingredient_id) WHERE (is_primary = true);


--
-- TOC entry 5021 (class 1259 OID 24735)
-- Name: idx_product_additives_additive; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_product_additives_additive ON public.product_additives USING btree (additive_id);


--
-- TOC entry 5022 (class 1259 OID 24736)
-- Name: idx_product_additives_branded_ingredient; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_product_additives_branded_ingredient ON public.product_additives USING btree (branded_ingredient_id);


--
-- TOC entry 5001 (class 1259 OID 24653)
-- Name: idx_product_images_branded_ingredient; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_product_images_branded_ingredient ON public.product_images USING btree (branded_ingredient_id);


--
-- TOC entry 5011 (class 1259 OID 24701)
-- Name: idx_product_nutrients_branded_ingredient; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_product_nutrients_branded_ingredient ON public.product_nutrients USING btree (branded_ingredient_id);


--
-- TOC entry 5012 (class 1259 OID 24702)
-- Name: idx_product_nutrients_nutrient; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_product_nutrients_nutrient ON public.product_nutrients USING btree (nutrient_id);


--
-- TOC entry 4963 (class 1259 OID 17787)
-- Name: idx_recipe_ingredients_branded_ingredient_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_recipe_ingredients_branded_ingredient_id ON public.recipe_ingredients USING btree (branded_ingredient_id);


--
-- TOC entry 4964 (class 1259 OID 17786)
-- Name: idx_recipe_ingredients_recipe_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_recipe_ingredients_recipe_id ON public.recipe_ingredients USING btree (recipe_id);


--
-- TOC entry 4970 (class 1259 OID 17789)
-- Name: idx_recipe_media_recipe_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_recipe_media_recipe_id ON public.recipe_media USING btree (recipe_id);


--
-- TOC entry 4981 (class 1259 OID 17793)
-- Name: idx_recipe_sharing_family_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_recipe_sharing_family_id ON public.recipe_sharing USING btree (family_id);


--
-- TOC entry 4982 (class 1259 OID 17792)
-- Name: idx_recipe_sharing_recipe_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_recipe_sharing_recipe_id ON public.recipe_sharing USING btree (recipe_id);


--
-- TOC entry 4967 (class 1259 OID 17788)
-- Name: idx_recipe_steps_recipe_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_recipe_steps_recipe_id ON public.recipe_steps USING btree (recipe_id);


--
-- TOC entry 4975 (class 1259 OID 17790)
-- Name: idx_recipe_tags_recipe_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_recipe_tags_recipe_id ON public.recipe_tags USING btree (recipe_id);


--
-- TOC entry 4976 (class 1259 OID 17791)
-- Name: idx_recipe_tags_tag_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_recipe_tags_tag_id ON public.recipe_tags USING btree (tag_id);


--
-- TOC entry 4942 (class 1259 OID 17782)
-- Name: idx_recipes_created_by_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_recipes_created_by_user_id ON public.recipes USING btree (created_by_user_id);


--
-- TOC entry 4943 (class 1259 OID 17783)
-- Name: idx_recipes_cuisine_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_recipes_cuisine_id ON public.recipes USING btree (cuisine_id);


--
-- TOC entry 5069 (class 2620 OID 24762)
-- Name: ingredient_lists update_ingredient_lists_modtime; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_ingredient_lists_modtime BEFORE UPDATE ON public.ingredient_lists FOR EACH ROW EXECUTE FUNCTION public.update_modified_column();


--
-- TOC entry 5068 (class 2620 OID 24761)
-- Name: product_nutrients update_product_nutrients_modtime; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_product_nutrients_modtime BEFORE UPDATE ON public.product_nutrients FOR EACH ROW EXECUTE FUNCTION public.update_modified_column();


--
-- TOC entry 5067 (class 2620 OID 17801)
-- Name: recipes update_recipes_modtime; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_recipes_modtime BEFORE UPDATE ON public.recipes FOR EACH ROW EXECUTE FUNCTION public.update_modified_column();


--
-- TOC entry 5066 (class 2620 OID 17800)
-- Name: users update_users_modtime; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_users_modtime BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_modified_column();


--
-- TOC entry 5055 (class 2606 OID 24606)
-- Name: additives additives_added_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.additives
    ADD CONSTRAINT additives_added_by_user_id_fkey FOREIGN KEY (added_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 5056 (class 2606 OID 24601)
-- Name: additives additives_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.additives
    ADD CONSTRAINT additives_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.additive_categories(id);


--
-- TOC entry 5038 (class 2606 OID 17645)
-- Name: base_ingredients base_ingredients_added_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.base_ingredients
    ADD CONSTRAINT base_ingredients_added_by_user_id_fkey FOREIGN KEY (added_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 5039 (class 2606 OID 17640)
-- Name: base_ingredients base_ingredients_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.base_ingredients
    ADD CONSTRAINT base_ingredients_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.ingredient_categories(id);


--
-- TOC entry 5040 (class 2606 OID 17672)
-- Name: branded_ingredients branded_ingredients_added_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branded_ingredients
    ADD CONSTRAINT branded_ingredients_added_by_user_id_fkey FOREIGN KEY (added_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 5041 (class 2606 OID 17662)
-- Name: branded_ingredients branded_ingredients_base_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branded_ingredients
    ADD CONSTRAINT branded_ingredients_base_ingredient_id_fkey FOREIGN KEY (base_ingredient_id) REFERENCES public.base_ingredients(id) ON DELETE CASCADE;


--
-- TOC entry 5042 (class 2606 OID 17667)
-- Name: branded_ingredients branded_ingredients_brand_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.branded_ingredients
    ADD CONSTRAINT branded_ingredients_brand_id_fkey FOREIGN KEY (brand_id) REFERENCES public.brands(id) ON DELETE CASCADE;


--
-- TOC entry 5037 (class 2606 OID 17625)
-- Name: brands brands_added_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.brands
    ADD CONSTRAINT brands_added_by_user_id_fkey FOREIGN KEY (added_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 5032 (class 2606 OID 17554)
-- Name: families families_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.families
    ADD CONSTRAINT families_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 5033 (class 2606 OID 17570)
-- Name: family_members family_members_family_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.family_members
    ADD CONSTRAINT family_members_family_id_fkey FOREIGN KEY (family_id) REFERENCES public.families(id) ON DELETE CASCADE;


--
-- TOC entry 5034 (class 2606 OID 17575)
-- Name: family_members family_members_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.family_members
    ADD CONSTRAINT family_members_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 5064 (class 2606 OID 24750)
-- Name: ingredient_lists ingredient_lists_branded_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ingredient_lists
    ADD CONSTRAINT ingredient_lists_branded_ingredient_id_fkey FOREIGN KEY (branded_ingredient_id) REFERENCES public.branded_ingredients(id) ON DELETE CASCADE;


--
-- TOC entry 5065 (class 2606 OID 24755)
-- Name: ingredient_lists ingredient_lists_extracted_from_image_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ingredient_lists
    ADD CONSTRAINT ingredient_lists_extracted_from_image_fkey FOREIGN KEY (extracted_from_image) REFERENCES public.product_images(id) ON DELETE SET NULL;


--
-- TOC entry 5058 (class 2606 OID 24674)
-- Name: nutrients nutrients_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nutrients
    ADD CONSTRAINT nutrients_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.nutrient_categories(id) ON DELETE SET NULL;


--
-- TOC entry 5062 (class 2606 OID 24725)
-- Name: product_additives product_additives_additive_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_additives
    ADD CONSTRAINT product_additives_additive_id_fkey FOREIGN KEY (additive_id) REFERENCES public.additives(id) ON DELETE CASCADE;


--
-- TOC entry 5063 (class 2606 OID 24730)
-- Name: product_additives product_additives_branded_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_additives
    ADD CONSTRAINT product_additives_branded_ingredient_id_fkey FOREIGN KEY (branded_ingredient_id) REFERENCES public.branded_ingredients(id) ON DELETE CASCADE;


--
-- TOC entry 5057 (class 2606 OID 24647)
-- Name: product_images product_images_branded_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_images
    ADD CONSTRAINT product_images_branded_ingredient_id_fkey FOREIGN KEY (branded_ingredient_id) REFERENCES public.branded_ingredients(id) ON DELETE CASCADE;


--
-- TOC entry 5059 (class 2606 OID 24691)
-- Name: product_nutrients product_nutrients_branded_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_nutrients
    ADD CONSTRAINT product_nutrients_branded_ingredient_id_fkey FOREIGN KEY (branded_ingredient_id) REFERENCES public.branded_ingredients(id) ON DELETE CASCADE;


--
-- TOC entry 5060 (class 2606 OID 24696)
-- Name: product_nutrients product_nutrients_nutrient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_nutrients
    ADD CONSTRAINT product_nutrients_nutrient_id_fkey FOREIGN KEY (nutrient_id) REFERENCES public.nutrients(id) ON DELETE CASCADE;


--
-- TOC entry 5043 (class 2606 OID 17697)
-- Name: recipe_ingredients recipe_ingredients_branded_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipe_ingredients
    ADD CONSTRAINT recipe_ingredients_branded_ingredient_id_fkey FOREIGN KEY (branded_ingredient_id) REFERENCES public.branded_ingredients(id) ON DELETE RESTRICT;


--
-- TOC entry 5044 (class 2606 OID 17692)
-- Name: recipe_ingredients recipe_ingredients_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipe_ingredients
    ADD CONSTRAINT recipe_ingredients_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- TOC entry 5045 (class 2606 OID 17702)
-- Name: recipe_ingredients recipe_ingredients_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipe_ingredients
    ADD CONSTRAINT recipe_ingredients_unit_id_fkey FOREIGN KEY (unit_id) REFERENCES public.units(id) ON DELETE SET NULL;


--
-- TOC entry 5047 (class 2606 OID 17729)
-- Name: recipe_media recipe_media_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipe_media
    ADD CONSTRAINT recipe_media_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- TOC entry 5050 (class 2606 OID 17772)
-- Name: recipe_sharing recipe_sharing_family_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipe_sharing
    ADD CONSTRAINT recipe_sharing_family_id_fkey FOREIGN KEY (family_id) REFERENCES public.families(id) ON DELETE CASCADE;


--
-- TOC entry 5051 (class 2606 OID 17767)
-- Name: recipe_sharing recipe_sharing_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipe_sharing
    ADD CONSTRAINT recipe_sharing_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- TOC entry 5052 (class 2606 OID 17777)
-- Name: recipe_sharing recipe_sharing_shared_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipe_sharing
    ADD CONSTRAINT recipe_sharing_shared_by_user_id_fkey FOREIGN KEY (shared_by_user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 5046 (class 2606 OID 17715)
-- Name: recipe_steps recipe_steps_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipe_steps
    ADD CONSTRAINT recipe_steps_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- TOC entry 5048 (class 2606 OID 17748)
-- Name: recipe_tags recipe_tags_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipe_tags
    ADD CONSTRAINT recipe_tags_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- TOC entry 5049 (class 2606 OID 17753)
-- Name: recipe_tags recipe_tags_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipe_tags
    ADD CONSTRAINT recipe_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tags(id) ON DELETE CASCADE;


--
-- TOC entry 5035 (class 2606 OID 17599)
-- Name: recipes recipes_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipes
    ADD CONSTRAINT recipes_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 5036 (class 2606 OID 17604)
-- Name: recipes recipes_cuisine_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recipes
    ADD CONSTRAINT recipes_cuisine_id_fkey FOREIGN KEY (cuisine_id) REFERENCES public.cuisines(id);


--
-- TOC entry 5061 (class 2606 OID 24711)
-- Name: serving_info serving_info_branded_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.serving_info
    ADD CONSTRAINT serving_info_branded_ingredient_id_fkey FOREIGN KEY (branded_ingredient_id) REFERENCES public.branded_ingredients(id) ON DELETE CASCADE;


--
-- TOC entry 5053 (class 2606 OID 17829)
-- Name: user_permissions user_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT user_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.admin_permissions(id) ON DELETE CASCADE;


--
-- TOC entry 5054 (class 2606 OID 17824)
-- Name: user_permissions user_permissions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT user_permissions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


-- Completed on 2025-04-29 18:11:51

--
-- PostgreSQL database dump complete
--

