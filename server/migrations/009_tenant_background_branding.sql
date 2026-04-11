ALTER TABLE public.tenants
ADD COLUMN IF NOT EXISTS background_color varchar;

ALTER TABLE public.tenants
ADD COLUMN IF NOT EXISTS widget_background_color varchar;

NOTIFY pgrst, 'reload schema';
