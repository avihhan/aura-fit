-- Nutrition targets expansion:
-- 1) Rich meal input for nutrition logs
-- 2) Persisted questionnaire fields used for calorie/protein recommendations

ALTER TABLE public.nutrition_logs
ADD COLUMN IF NOT EXISTS meal_items text;

CREATE TABLE IF NOT EXISTS public.user_nutrition_profiles (
    id                bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id         bigint NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    user_id           bigint NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    sex               varchar NOT NULL,
    age_years         integer NOT NULL,
    activity_level    varchar NOT NULL,
    goal              varchar NOT NULL,
    created_at        timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT user_nutrition_profiles_user_key UNIQUE (tenant_id, user_id),
    CONSTRAINT user_nutrition_profiles_sex_check CHECK (sex IN ('male', 'female')),
    CONSTRAINT user_nutrition_profiles_age_check CHECK (age_years >= 13 AND age_years <= 120),
    CONSTRAINT user_nutrition_profiles_activity_check CHECK (
        activity_level IN ('sedentary', 'light', 'moderate', 'very_active', 'extra_active')
    ),
    CONSTRAINT user_nutrition_profiles_goal_check CHECK (goal IN ('lose', 'maintain', 'gain'))
);

CREATE INDEX IF NOT EXISTS idx_user_nutrition_profiles_tenant_user
ON public.user_nutrition_profiles (tenant_id, user_id);
