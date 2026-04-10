-- Health UX expansion:
-- 1) Body metrics height as feet/inches
-- 2) Master email notification toggle

ALTER TABLE public.body_metrics
ADD COLUMN IF NOT EXISTS height_feet integer,
ADD COLUMN IF NOT EXISTS height_inches integer;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'body_metrics_height_feet_check'
    ) THEN
        ALTER TABLE public.body_metrics
        ADD CONSTRAINT body_metrics_height_feet_check
        CHECK (height_feet IS NULL OR (height_feet >= 0 AND height_feet <= 9));
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'body_metrics_height_inches_check'
    ) THEN
        ALTER TABLE public.body_metrics
        ADD CONSTRAINT body_metrics_height_inches_check
        CHECK (height_inches IS NULL OR (height_inches >= 0 AND height_inches <= 11));
    END IF;
END $$;

-- Backfill feet/inches from legacy "height" numeric field where possible.
-- Heuristic:
-- - If height >= 96, treat as centimeters.
-- - Otherwise, treat as inches.
UPDATE public.body_metrics
SET
    height_feet = FLOOR(
        CASE
            WHEN height >= 96 THEN (height / 2.54)
            ELSE height
        END / 12
    )::integer,
    height_inches = ROUND(
        CASE
            WHEN height >= 96 THEN (height / 2.54)
            ELSE height
        END - FLOOR(
            CASE
                WHEN height >= 96 THEN (height / 2.54)
                ELSE height
            END / 12
        ) * 12
    )::integer
WHERE
    height IS NOT NULL
    AND (height_feet IS NULL OR height_inches IS NULL);

ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS email_notifications_enabled boolean NOT NULL DEFAULT true;
