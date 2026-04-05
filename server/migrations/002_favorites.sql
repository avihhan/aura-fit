-- Favorites table: users can favorite exercises for quick access.

CREATE SEQUENCE IF NOT EXISTS favorites_id_seq;

CREATE TABLE IF NOT EXISTS public.favorites (
    id          bigint    NOT NULL DEFAULT nextval('favorites_id_seq'::regclass),
    tenant_id   bigint    NOT NULL,
    user_id     bigint    NOT NULL,
    exercise_id bigint    NOT NULL,
    created_at  timestamp DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT favorites_pkey PRIMARY KEY (id),
    CONSTRAINT favorites_tenant_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id),
    CONSTRAINT favorites_user_fkey FOREIGN KEY (user_id) REFERENCES public.users(id),
    CONSTRAINT favorites_exercise_fkey FOREIGN KEY (exercise_id) REFERENCES public.exercises(id) ON DELETE CASCADE,
    CONSTRAINT favorites_unique UNIQUE (user_id, exercise_id)
);
