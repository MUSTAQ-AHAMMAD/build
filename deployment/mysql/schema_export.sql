-- ==============================================================================
-- BUILD+ ENTERPRISE PORTAL — COMPLETE MYSQL PRODUCTION SCHEMA DDL EXPORT
-- Engine: InnoDB | Charset: utf8mb4 | Collation: utf8mb4_unicode_ci
-- ==============================================================================

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

-- ------------------------------------------------------------------------------
-- SCHEMA DDL
-- ------------------------------------------------------------------------------

-- ------------------------------------------------------------------------------
-- Migration: contenttypes.0001_initial
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Create model ContentType
--
CREATE TABLE "django_content_type" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "app_label" varchar(100) NOT NULL, "model" varchar(100) NOT NULL);
--
-- Alter unique_together for contenttype (1 constraint(s))
--
CREATE UNIQUE INDEX "django_content_type_app_label_model_76bd3d3b_uniq" ON "django_content_type" ("app_label", "model");
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: auth.0001_initial
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Create model Permission
--
CREATE TABLE "auth_permission" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(50) NOT NULL, "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "codename" varchar(100) NOT NULL);
--
-- Create model Group
--
CREATE TABLE "auth_group" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(80) NOT NULL UNIQUE);
CREATE TABLE "auth_group_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model User
--
CREATE TABLE "auth_user" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "password" varchar(128) NOT NULL, "last_login" datetime NOT NULL, "is_superuser" bool NOT NULL, "username" varchar(30) NOT NULL UNIQUE, "first_name" varchar(30) NOT NULL, "last_name" varchar(30) NOT NULL, "email" varchar(75) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL);
CREATE TABLE "auth_user_groups" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "auth_user_user_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE UNIQUE INDEX "auth_permission_content_type_id_codename_01ab375a_uniq" ON "auth_permission" ("content_type_id", "codename");
CREATE INDEX "auth_permission_content_type_id_2f476e4b" ON "auth_permission" ("content_type_id");
CREATE UNIQUE INDEX "auth_group_permissions_group_id_permission_id_0cd325b0_uniq" ON "auth_group_permissions" ("group_id", "permission_id");
CREATE INDEX "auth_group_permissions_group_id_b120cbf9" ON "auth_group_permissions" ("group_id");
CREATE INDEX "auth_group_permissions_permission_id_84c5c92e" ON "auth_group_permissions" ("permission_id");
CREATE UNIQUE INDEX "auth_user_groups_user_id_group_id_94350c0c_uniq" ON "auth_user_groups" ("user_id", "group_id");
CREATE INDEX "auth_user_groups_user_id_6a12ed8b" ON "auth_user_groups" ("user_id");
CREATE INDEX "auth_user_groups_group_id_97559544" ON "auth_user_groups" ("group_id");
CREATE UNIQUE INDEX "auth_user_user_permissions_user_id_permission_id_14a6b632_uniq" ON "auth_user_user_permissions" ("user_id", "permission_id");
CREATE INDEX "auth_user_user_permissions_user_id_a95ead1b" ON "auth_user_user_permissions" ("user_id");
CREATE INDEX "auth_user_user_permissions_permission_id_1fbb5f2c" ON "auth_user_user_permissions" ("permission_id");
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: admin.0001_initial
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Create model LogEntry
--
CREATE TABLE "django_admin_log" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "action_time" datetime NOT NULL, "object_id" text NULL, "object_repr" varchar(200) NOT NULL, "action_flag" smallint unsigned NOT NULL CHECK ("action_flag" >= 0), "change_message" text NOT NULL, "content_type_id" integer NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "django_admin_log_content_type_id_c4bce8eb" ON "django_admin_log" ("content_type_id");
CREATE INDEX "django_admin_log_user_id_c564eba6" ON "django_admin_log" ("user_id");
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: admin.0002_logentry_remove_auto_add
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Alter field action_time on logentry
--
CREATE TABLE "new__django_admin_log" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "action_time" datetime NOT NULL, "object_id" text NULL, "object_repr" varchar(200) NOT NULL, "action_flag" smallint unsigned NOT NULL CHECK ("action_flag" >= 0), "change_message" text NOT NULL, "content_type_id" integer NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__django_admin_log" ("id", "object_id", "object_repr", "action_flag", "change_message", "content_type_id", "user_id", "action_time") SELECT "id", "object_id", "object_repr", "action_flag", "change_message", "content_type_id", "user_id", "action_time" FROM "django_admin_log";
DROP TABLE "django_admin_log";
ALTER TABLE "new__django_admin_log" RENAME TO "django_admin_log";
CREATE INDEX "django_admin_log_content_type_id_c4bce8eb" ON "django_admin_log" ("content_type_id");
CREATE INDEX "django_admin_log_user_id_c564eba6" ON "django_admin_log" ("user_id");
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: admin.0003_logentry_add_action_flag_choices
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Alter field action_flag on logentry
--
-- (no-op)
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: crm.0001_initial
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Create model LeadSource
--
CREATE TABLE "crm_leadsource" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL UNIQUE, "slug" varchar(120) NOT NULL UNIQUE, "is_active" bool NOT NULL, "created_at" datetime NOT NULL);
--
-- Create model Lead
--
CREATE TABLE "crm_lead" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "lead_id" varchar(32) NOT NULL UNIQUE, "first_name" varchar(100) NOT NULL, "last_name" varchar(100) NOT NULL, "company_name" varchar(150) NOT NULL, "phone" varchar(25) NOT NULL, "alternate_phone" varchar(25) NOT NULL, "email" varchar(254) NOT NULL, "whatsapp_number" varchar(25) NOT NULL, "preferred_contact_method" varchar(20) NOT NULL, "customer_type" varchar(30) NOT NULL, "service_category" varchar(40) NOT NULL, "service_type" varchar(60) NOT NULL, "property_type" varchar(40) NOT NULL, "property_location" varchar(255) NOT NULL, "city" varchar(100) NOT NULL, "area_locality" varchar(120) NOT NULL, "approximate_property_area" varchar(80) NOT NULL, "unit" varchar(20) NOT NULL, "project_description" text NOT NULL, "estimated_budget" varchar(100) NOT NULL, "budget_range" varchar(100) NOT NULL, "expected_project_value" decimal NULL, "final_project_value" decimal NULL, "expected_closing_date" date NULL, "won_date" date NULL, "lost_reason" varchar(40) NOT NULL, "lost_notes" text NOT NULL, "on_hold_reason" text NOT NULL, "lead_source_text" varchar(100) NOT NULL, "priority" varchar(10) NOT NULL, "status" varchar(30) NOT NULL, "next_follow_up_date" datetime NULL, "is_deleted" bool NOT NULL, "deleted_at" datetime NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "assigned_to_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "deleted_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "lead_source_id" bigint NULL REFERENCES "crm_leadsource" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model FollowUp
--
CREATE TABLE "crm_followup" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "follow_up_date" date NOT NULL, "follow_up_time" time NULL, "follow_up_type" varchar(30) NOT NULL, "subject" varchar(200) NOT NULL, "notes" text NOT NULL, "outcome" text NOT NULL, "next_follow_up_date" datetime NULL, "completed" bool NOT NULL, "completed_at" datetime NULL, "created_at" datetime NOT NULL, "assigned_to_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "lead_id" bigint NOT NULL REFERENCES "crm_lead" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Estimate
--
CREATE TABLE "crm_estimate" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "estimate_number" varchar(50) NOT NULL UNIQUE, "estimate_date" date NOT NULL, "description" varchar(255) NOT NULL, "estimated_amount" decimal NOT NULL, "tax_amount" decimal NOT NULL, "total_amount" decimal NOT NULL, "valid_until" date NULL, "status" varchar(30) NOT NULL, "notes" text NOT NULL, "created_at" datetime NOT NULL, "lead_id" bigint NOT NULL REFERENCES "crm_lead" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model LeadActivity
--
CREATE TABLE "crm_leadactivity" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "activity_type" varchar(30) NOT NULL, "title" varchar(200) NOT NULL, "description" text NOT NULL, "created_at" datetime NOT NULL, "lead_id" bigint NOT NULL REFERENCES "crm_lead" ("id") DEFERRABLE INITIALLY DEFERRED, "performed_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model LeadNote
--
CREATE TABLE "crm_leadnote" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "note" text NOT NULL, "created_at" datetime NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "lead_id" bigint NOT NULL REFERENCES "crm_lead" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model SiteVisit
--
CREATE TABLE "crm_sitevisit" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "site_address" varchar(255) NOT NULL, "visit_date" date NOT NULL, "visit_time" time NULL, "site_contact" varchar(150) NOT NULL, "property_type" varchar(100) NOT NULL, "site_condition" text NOT NULL, "requirements" text NOT NULL, "measurements" text NOT NULL, "notes" text NOT NULL, "status" varchar(20) NOT NULL, "created_at" datetime NOT NULL, "assigned_staff_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "lead_id" bigint NOT NULL REFERENCES "crm_lead" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create index crm_lead_status_317d75_idx on field(s) status, priority of model lead
--
CREATE INDEX "crm_lead_status_317d75_idx" ON "crm_lead" ("status", "priority");
--
-- Create index crm_lead_city_bff327_idx on field(s) city, service_category of model lead
--
CREATE INDEX "crm_lead_city_bff327_idx" ON "crm_lead" ("city", "service_category");
CREATE INDEX "crm_lead_phone_3f600b80" ON "crm_lead" ("phone");
CREATE INDEX "crm_lead_email_0245eb29" ON "crm_lead" ("email");
CREATE INDEX "crm_lead_service_category_944e25cd" ON "crm_lead" ("service_category");
CREATE INDEX "crm_lead_service_type_4d5e2dd4" ON "crm_lead" ("service_type");
CREATE INDEX "crm_lead_city_a34f010c" ON "crm_lead" ("city");
CREATE INDEX "crm_lead_priority_af0316bd" ON "crm_lead" ("priority");
CREATE INDEX "crm_lead_status_526ebf3b" ON "crm_lead" ("status");
CREATE INDEX "crm_lead_next_follow_up_date_88153fc6" ON "crm_lead" ("next_follow_up_date");
CREATE INDEX "crm_lead_is_deleted_4fb4662a" ON "crm_lead" ("is_deleted");
CREATE INDEX "crm_lead_created_at_bab55e89" ON "crm_lead" ("created_at");
CREATE INDEX "crm_lead_assigned_to_id_d2e8614f" ON "crm_lead" ("assigned_to_id");
CREATE INDEX "crm_lead_deleted_by_id_d3b32d7a" ON "crm_lead" ("deleted_by_id");
CREATE INDEX "crm_lead_lead_source_id_6dab1962" ON "crm_lead" ("lead_source_id");
CREATE INDEX "crm_followup_assigned_to_id_7ac008a5" ON "crm_followup" ("assigned_to_id");
CREATE INDEX "crm_followup_lead_id_c3df1e23" ON "crm_followup" ("lead_id");
CREATE INDEX "crm_estimate_lead_id_82e58b3f" ON "crm_estimate" ("lead_id");
CREATE INDEX "crm_leadactivity_lead_id_36437971" ON "crm_leadactivity" ("lead_id");
CREATE INDEX "crm_leadactivity_performed_by_id_c43dee55" ON "crm_leadactivity" ("performed_by_id");
CREATE INDEX "crm_leadnote_created_by_id_285fadd4" ON "crm_leadnote" ("created_by_id");
CREATE INDEX "crm_leadnote_lead_id_0eecac34" ON "crm_leadnote" ("lead_id");
CREATE INDEX "crm_sitevisit_assigned_staff_id_2fb7f7d0" ON "crm_sitevisit" ("assigned_staff_id");
CREATE INDEX "crm_sitevisit_lead_id_423b8d23" ON "crm_sitevisit" ("lead_id");
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: ai_assistant.0001_initial
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Create model AIChatbotSettings
--
CREATE TABLE "ai_assistant_aichatbotsettings" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "is_enabled" bool NOT NULL, "ai_name" varchar(100) NOT NULL, "welcome_message" text NOT NULL, "business_description" text NOT NULL, "contact_phone" varchar(50) NOT NULL, "whatsapp_number" varchar(50) NOT NULL, "working_hours" varchar(150) NOT NULL, "emergency_message" text NOT NULL, "fallback_message" text NOT NULL, "human_handoff_message" text NOT NULL, "enable_lead_capture" bool NOT NULL, "enable_ai_summary" bool NOT NULL, "enable_ai_priority" bool NOT NULL, "updated_at" datetime NOT NULL);
--
-- Create model AIKnowledgeItem
--
CREATE TABLE "ai_assistant_aiknowledgeitem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "category" varchar(40) NOT NULL, "topic" varchar(200) NOT NULL, "keywords" varchar(255) NOT NULL, "approved_content" text NOT NULL, "who_is_it_for" varchar(255) NOT NULL, "typical_process" text NOT NULL, "pricing_guideline" varchar(255) NOT NULL, "safety_boundary" varchar(255) NOT NULL, "is_active" bool NOT NULL, "display_order" integer unsigned NOT NULL CHECK ("display_order" >= 0), "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL);
--
-- Create model ChatSession
--
CREATE TABLE "ai_assistant_chatsession" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "session_id" varchar(100) NOT NULL UNIQUE, "visitor_name" varchar(150) NOT NULL, "visitor_phone" varchar(50) NOT NULL, "visitor_email" varchar(254) NOT NULL, "visitor_whatsapp" varchar(50) NOT NULL, "visitor_location" varchar(150) NOT NULL, "service_category" varchar(60) NOT NULL, "service_type" varchar(100) NOT NULL, "property_type" varchar(100) NOT NULL, "property_condition" varchar(100) NOT NULL, "approximate_area" varchar(100) NOT NULL, "project_description" text NOT NULL, "estimated_budget" varchar(100) NOT NULL, "timeline" varchar(100) NOT NULL, "is_nri" bool NOT NULL, "site_visit_requested" bool NOT NULL, "preferred_site_visit_date" date NULL, "detected_intent" varchar(150) NOT NULL, "ai_lead_summary" text NOT NULL, "suggested_priority" varchar(20) NOT NULL, "status" varchar(30) NOT NULL, "human_agent_active" bool NOT NULL, "ip_address" char(39) NULL, "user_agent" text NOT NULL, "started_at" datetime NOT NULL, "last_activity_at" datetime NOT NULL, "assigned_human_agent_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "lead_id" bigint NULL REFERENCES "crm_lead" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model ChatMessage
--
CREATE TABLE "ai_assistant_chatmessage" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "sender_type" varchar(20) NOT NULL, "sender_name" varchar(100) NOT NULL, "content" text NOT NULL, "quick_actions_json" text NOT NULL CHECK ((JSON_VALID("quick_actions_json") OR "quick_actions_json" IS NULL)), "metadata" text NOT NULL CHECK ((JSON_VALID("metadata") OR "metadata" IS NULL)), "created_at" datetime NOT NULL, "session_id" bigint NOT NULL REFERENCES "ai_assistant_chatsession" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "ai_assistant_aiknowledgeitem_category_43ee2c2f" ON "ai_assistant_aiknowledgeitem" ("category");
CREATE INDEX "ai_assistant_chatsession_status_3abe6673" ON "ai_assistant_chatsession" ("status");
CREATE INDEX "ai_assistant_chatsession_assigned_human_agent_id_3c7febfc" ON "ai_assistant_chatsession" ("assigned_human_agent_id");
CREATE INDEX "ai_assistant_chatsession_lead_id_6144ca4d" ON "ai_assistant_chatsession" ("lead_id");
CREATE INDEX "ai_assistant_chatmessage_session_id_924760f4" ON "ai_assistant_chatmessage" ("session_id");
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: auth.0002_alter_permission_name_max_length
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Alter field name on permission
--
CREATE TABLE "new__auth_permission" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(255) NOT NULL, "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "codename" varchar(100) NOT NULL);
INSERT INTO "new__auth_permission" ("id", "content_type_id", "codename", "name") SELECT "id", "content_type_id", "codename", "name" FROM "auth_permission";
DROP TABLE "auth_permission";
ALTER TABLE "new__auth_permission" RENAME TO "auth_permission";
CREATE UNIQUE INDEX "auth_permission_content_type_id_codename_01ab375a_uniq" ON "auth_permission" ("content_type_id", "codename");
CREATE INDEX "auth_permission_content_type_id_2f476e4b" ON "auth_permission" ("content_type_id");
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: auth.0003_alter_user_email_max_length
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Alter field email on user
--
CREATE TABLE "new__auth_user" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "email" varchar(254) NOT NULL, "password" varchar(128) NOT NULL, "last_login" datetime NOT NULL, "is_superuser" bool NOT NULL, "username" varchar(30) NOT NULL UNIQUE, "first_name" varchar(30) NOT NULL, "last_name" varchar(30) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL);
INSERT INTO "new__auth_user" ("id", "password", "last_login", "is_superuser", "username", "first_name", "last_name", "is_staff", "is_active", "date_joined", "email") SELECT "id", "password", "last_login", "is_superuser", "username", "first_name", "last_name", "is_staff", "is_active", "date_joined", "email" FROM "auth_user";
DROP TABLE "auth_user";
ALTER TABLE "new__auth_user" RENAME TO "auth_user";
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: auth.0004_alter_user_username_opts
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Alter field username on user
--
-- (no-op)
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: auth.0005_alter_user_last_login_null
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Alter field last_login on user
--
CREATE TABLE "new__auth_user" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "last_login" datetime NULL, "password" varchar(128) NOT NULL, "is_superuser" bool NOT NULL, "username" varchar(30) NOT NULL UNIQUE, "first_name" varchar(30) NOT NULL, "last_name" varchar(30) NOT NULL, "email" varchar(254) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL);
INSERT INTO "new__auth_user" ("id", "password", "is_superuser", "username", "first_name", "last_name", "email", "is_staff", "is_active", "date_joined", "last_login") SELECT "id", "password", "is_superuser", "username", "first_name", "last_name", "email", "is_staff", "is_active", "date_joined", "last_login" FROM "auth_user";
DROP TABLE "auth_user";
ALTER TABLE "new__auth_user" RENAME TO "auth_user";
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: contenttypes.0002_remove_content_type_name
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Change Meta options on contenttype
--
-- (no-op)
--
-- Alter field name on contenttype
--
CREATE TABLE "new__django_content_type" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NULL, "app_label" varchar(100) NOT NULL, "model" varchar(100) NOT NULL);
INSERT INTO "new__django_content_type" ("id", "app_label", "model", "name") SELECT "id", "app_label", "model", "name" FROM "django_content_type";
DROP TABLE "django_content_type";
ALTER TABLE "new__django_content_type" RENAME TO "django_content_type";
CREATE UNIQUE INDEX "django_content_type_app_label_model_76bd3d3b_uniq" ON "django_content_type" ("app_label", "model");
--
-- Raw Python operation
--
-- THIS OPERATION CANNOT BE WRITTEN AS SQL
--
-- Remove field name from contenttype
--
ALTER TABLE "django_content_type" DROP COLUMN "name";
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: auth.0007_alter_validators_add_error_messages
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Alter field username on user
--
-- (no-op)
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: auth.0008_alter_user_username_max_length
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Alter field username on user
--
CREATE TABLE "new__auth_user" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "username" varchar(150) NOT NULL UNIQUE, "password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "first_name" varchar(30) NOT NULL, "last_name" varchar(30) NOT NULL, "email" varchar(254) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL);
INSERT INTO "new__auth_user" ("id", "password", "last_login", "is_superuser", "first_name", "last_name", "email", "is_staff", "is_active", "date_joined", "username") SELECT "id", "password", "last_login", "is_superuser", "first_name", "last_name", "email", "is_staff", "is_active", "date_joined", "username" FROM "auth_user";
DROP TABLE "auth_user";
ALTER TABLE "new__auth_user" RENAME TO "auth_user";
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: auth.0009_alter_user_last_name_max_length
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Alter field last_name on user
--
CREATE TABLE "new__auth_user" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "last_name" varchar(150) NOT NULL, "password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "username" varchar(150) NOT NULL UNIQUE, "first_name" varchar(30) NOT NULL, "email" varchar(254) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL);
INSERT INTO "new__auth_user" ("id", "password", "last_login", "is_superuser", "username", "first_name", "email", "is_staff", "is_active", "date_joined", "last_name") SELECT "id", "password", "last_login", "is_superuser", "username", "first_name", "email", "is_staff", "is_active", "date_joined", "last_name" FROM "auth_user";
DROP TABLE "auth_user";
ALTER TABLE "new__auth_user" RENAME TO "auth_user";
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: auth.0010_alter_group_name_max_length
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Alter field name on group
--
CREATE TABLE "new__auth_group" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(150) NOT NULL UNIQUE);
INSERT INTO "new__auth_group" ("id", "name") SELECT "id", "name" FROM "auth_group";
DROP TABLE "auth_group";
ALTER TABLE "new__auth_group" RENAME TO "auth_group";
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: auth.0011_update_proxy_permissions
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Raw Python operation
--
-- THIS OPERATION CANNOT BE WRITTEN AS SQL
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: auth.0012_alter_user_first_name_max_length
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Alter field first_name on user
--
CREATE TABLE "new__auth_user" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "first_name" varchar(150) NOT NULL, "password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "username" varchar(150) NOT NULL UNIQUE, "last_name" varchar(150) NOT NULL, "email" varchar(254) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL);
INSERT INTO "new__auth_user" ("id", "password", "last_login", "is_superuser", "username", "last_name", "email", "is_staff", "is_active", "date_joined", "first_name") SELECT "id", "password", "last_login", "is_superuser", "username", "last_name", "email", "is_staff", "is_active", "date_joined", "first_name" FROM "auth_user";
DROP TABLE "auth_user";
ALTER TABLE "new__auth_user" RENAME TO "auth_user";
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: blog.0001_initial
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Create model BlogCategory
--
CREATE TABLE "blog_blogcategory" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(120) NOT NULL UNIQUE, "slug" varchar(150) NOT NULL UNIQUE, "description" text NOT NULL, "status" varchar(15) NOT NULL, "display_order" integer unsigned NOT NULL CHECK ("display_order" >= 0), "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL);
--
-- Create model BlogPost
--
CREATE TABLE "blog_blogpost" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(255) NOT NULL UNIQUE, "slug" varchar(280) NOT NULL UNIQUE, "author" varchar(100) NOT NULL, "short_description" text NOT NULL, "content" text NOT NULL, "featured_image" varchar(100) NULL, "status" varchar(15) NOT NULL, "featured" bool NOT NULL, "published_date" datetime NULL, "related_service_type" varchar(40) NOT NULL, "seo_title" varchar(180) NOT NULL, "seo_description" varchar(255) NOT NULL, "seo_keywords" varchar(255) NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "category_id" bigint NOT NULL REFERENCES "blog_blogcategory" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "blog_blogpost_category_id_0e9835dd" ON "blog_blogpost" ("category_id");
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: core.0001_initial
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Create model FAQ
--
CREATE TABLE "core_faq" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "category" varchar(30) NOT NULL, "question" varchar(300) NOT NULL, "answer" text NOT NULL, "display_order" integer unsigned NOT NULL CHECK ("display_order" >= 0), "is_published" bool NOT NULL);
--
-- Create model TeamMember
--
CREATE TABLE "core_teammember" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "role" varchar(100) NOT NULL, "bio" text NOT NULL, "photo" varchar(100) NULL, "display_order" integer unsigned NOT NULL CHECK ("display_order" >= 0));
--
-- Create model Testimonial
--
CREATE TABLE "core_testimonial" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "client_name" varchar(100) NOT NULL, "client_title" varchar(150) NOT NULL, "service_rendered" varchar(100) NOT NULL, "feedback" text NOT NULL, "rating" integer unsigned NOT NULL CHECK ("rating" >= 0), "avatar" varchar(100) NULL, "is_featured" bool NOT NULL, "display_order" integer unsigned NOT NULL CHECK ("display_order" >= 0), "created_at" datetime NOT NULL);
--
-- Create model WebsiteSettings
--
CREATE TABLE "core_websitesettings" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "site_name" varchar(150) NOT NULL, "tagline" varchar(255) NOT NULL, "primary_phone" varchar(50) NOT NULL, "whatsapp_number" varchar(50) NOT NULL, "primary_email" varchar(254) NOT NULL, "office_address" text NOT NULL, "facebook_url" varchar(200) NOT NULL, "instagram_url" varchar(200) NOT NULL, "linkedin_url" varchar(200) NOT NULL, "years_experience" integer unsigned NOT NULL CHECK ("years_experience" >= 0), "projects_completed" integer unsigned NOT NULL CHECK ("projects_completed" >= 0), "happy_clients" integer unsigned NOT NULL CHECK ("happy_clients" >= 0), "service_cities" varchar(255) NOT NULL, "meta_description" text NOT NULL, "meta_keywords" varchar(255) NOT NULL, "updated_at" datetime NOT NULL);
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: enquiries.0001_initial
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Create model Enquiry
--
CREATE TABLE "enquiries_enquiry" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "enquiry_type" varchar(30) NOT NULL, "full_name" varchar(120) NOT NULL, "phone_number" varchar(30) NOT NULL, "email" varchar(254) NOT NULL, "city_location" varchar(150) NOT NULL, "property_type" varchar(100) NOT NULL, "approximate_area" varchar(60) NOT NULL, "message" text NOT NULL, "site_visit_requested" bool NOT NULL, "preferred_date" date NULL, "status" varchar(20) NOT NULL, "internal_notes" text NOT NULL, "assigned_engineer" varchar(100) NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL);
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: enquiries.0002_enquiry_enquiry_number
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Add field enquiry_number to enquiry
--
CREATE TABLE "new__enquiries_enquiry" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "enquiry_number" varchar(30) NOT NULL UNIQUE, "enquiry_type" varchar(30) NOT NULL, "full_name" varchar(120) NOT NULL, "phone_number" varchar(30) NOT NULL, "email" varchar(254) NOT NULL, "city_location" varchar(150) NOT NULL, "property_type" varchar(100) NOT NULL, "approximate_area" varchar(60) NOT NULL, "message" text NOT NULL, "site_visit_requested" bool NOT NULL, "preferred_date" date NULL, "status" varchar(20) NOT NULL, "internal_notes" text NOT NULL, "assigned_engineer" varchar(100) NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL);
INSERT INTO "new__enquiries_enquiry" ("id", "enquiry_type", "full_name", "phone_number", "email", "city_location", "property_type", "approximate_area", "message", "site_visit_requested", "preferred_date", "status", "internal_notes", "assigned_engineer", "created_at", "updated_at", "enquiry_number") SELECT "id", "enquiry_type", "full_name", "phone_number", "email", "city_location", "property_type", "approximate_area", "message", "site_visit_requested", "preferred_date", "status", "internal_notes", "assigned_engineer", "created_at", "updated_at", '' FROM "enquiries_enquiry";
DROP TABLE "enquiries_enquiry";
ALTER TABLE "new__enquiries_enquiry" RENAME TO "enquiries_enquiry";
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: services.0001_initial
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Create model ServiceCategory
--
CREATE TABLE "services_servicecategory" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(120) NOT NULL UNIQUE, "slug" varchar(150) NOT NULL UNIQUE, "short_description" text NOT NULL, "hero_title" varchar(200) NOT NULL, "hero_subtitle" text NOT NULL, "icon" varchar(50) NOT NULL, "display_order" integer unsigned NOT NULL CHECK ("display_order" >= 0), "is_active" bool NOT NULL);
--
-- Create model Service
--
CREATE TABLE "services_service" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(180) NOT NULL, "slug" varchar(200) NOT NULL UNIQUE, "short_description" text NOT NULL, "full_description" text NOT NULL, "service_icon" varchar(50) NOT NULL, "benefits" text NOT NULL, "process_steps" text NOT NULL, "hero_image" varchar(100) NULL, "featured" bool NOT NULL, "published" bool NOT NULL, "display_order" integer unsigned NOT NULL CHECK ("display_order" >= 0), "seo_title" varchar(180) NOT NULL, "seo_description" varchar(255) NOT NULL, "seo_keywords" varchar(255) NOT NULL, "category_id" bigint NOT NULL REFERENCES "services_servicecategory" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "services_service_category_id_e15f8b7e" ON "services_service" ("category_id");
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: projects.0001_initial
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Create model ProjectCategory
--
CREATE TABLE "projects_projectcategory" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL UNIQUE, "slug" varchar(120) NOT NULL UNIQUE, "display_order" integer unsigned NOT NULL CHECK ("display_order" >= 0));
--
-- Create model Project
--
CREATE TABLE "projects_project" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(220) NOT NULL, "slug" varchar(250) NOT NULL UNIQUE, "location" varchar(150) NOT NULL, "project_type" varchar(120) NOT NULL, "client_type" varchar(100) NOT NULL, "project_status" varchar(20) NOT NULL, "duration" varchar(50) NOT NULL, "built_up_area" varchar(50) NOT NULL, "overview" text NOT NULL, "scope_of_work" text NOT NULL, "challenges" text NOT NULL, "solutions" text NOT NULL, "main_image" varchar(100) NULL, "before_image" varchar(100) NULL, "after_image" varchar(100) NULL, "featured" bool NOT NULL, "published" bool NOT NULL, "display_order" integer unsigned NOT NULL CHECK ("display_order" >= 0), "created_at" datetime NOT NULL, "category_id" bigint NOT NULL REFERENCES "projects_projectcategory" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "projects_project_category_id_708edb98" ON "projects_project" ("category_id");
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: payments.0001_initial
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Create model PaymentGateway
--
CREATE TABLE "payments_paymentgateway" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(120) NOT NULL, "slug" varchar(150) NOT NULL UNIQUE, "provider_name" varchar(100) NOT NULL, "gateway_type" varchar(30) NOT NULL, "description" text NOT NULL, "is_active" bool NOT NULL, "is_default" bool NOT NULL, "is_test_mode" bool NOT NULL, "public_key" varchar(255) NOT NULL, "merchant_id" varchar(255) NOT NULL, "encrypted_secret_key" varchar(255) NOT NULL, "encrypted_api_key" varchar(255) NOT NULL, "checkout_url" varchar(500) NOT NULL, "webhook_url" varchar(500) NOT NULL, "custom_html" text NOT NULL, "custom_css" text NOT NULL, "custom_js" text NOT NULL, "success_url" varchar(255) NOT NULL, "failure_url" varchar(255) NOT NULL, "cancel_url" varchar(255) NOT NULL, "documentation_url" varchar(200) NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL);
--
-- Create model PaymentSettings
--
CREATE TABLE "payments_paymentsettings" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "company_name" varchar(200) NOT NULL, "company_address" text NOT NULL, "currency" varchar(10) NOT NULL, "currency_symbol" varchar(10) NOT NULL, "gst_enabled" bool NOT NULL, "gst_number" varchar(50) NOT NULL, "gst_percentage" decimal NOT NULL, "invoice_prefix" varchar(20) NOT NULL, "receipt_prefix" varchar(20) NOT NULL, "payment_request_prefix" varchar(20) NOT NULL, "is_test_mode_globally" bool NOT NULL, "webhook_secret" varchar(255) NOT NULL, "payment_terms" text NOT NULL, "refund_policy" text NOT NULL, "updated_at" datetime NOT NULL);
--
-- Create model UPIConfiguration
--
CREATE TABLE "payments_upiconfiguration" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "upi_id" varchar(120) NOT NULL, "merchant_name" varchar(150) NOT NULL, "display_name" varchar(150) NOT NULL, "qr_code_image" varchar(100) NULL, "bank_account_number" varchar(50) NOT NULL, "bank_ifsc_code" varchar(30) NOT NULL, "bank_name" varchar(100) NOT NULL, "bank_branch" varchar(100) NOT NULL, "payment_instructions" text NOT NULL, "is_active" bool NOT NULL, "updated_at" datetime NOT NULL);
--
-- Create model PaymentMethod
--
CREATE TABLE "payments_paymentmethod" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "method_type" varchar(30) NOT NULL, "display_name" varchar(150) NOT NULL, "description" varchar(255) NOT NULL, "instructions" text NOT NULL, "icon" varchar(50) NOT NULL, "is_active" bool NOT NULL, "sort_order" integer unsigned NOT NULL CHECK ("sort_order" >= 0), "gateway_id" bigint NULL REFERENCES "payments_paymentgateway" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model PaymentRequest
--
CREATE TABLE "payments_paymentrequest" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "uuid" char(32) NOT NULL UNIQUE, "payment_reference" varchar(40) NOT NULL UNIQUE, "customer_name" varchar(150) NOT NULL, "customer_email" varchar(254) NOT NULL, "customer_phone" varchar(30) NOT NULL, "payment_purpose" varchar(255) NOT NULL, "amount" decimal NOT NULL, "tax_amount" decimal NOT NULL, "discount_amount" decimal NOT NULL, "total_amount" decimal NOT NULL, "currency" varchar(10) NOT NULL, "status" varchar(20) NOT NULL, "due_date" date NULL, "expiry_date" date NULL, "notes" text NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "created_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "estimate_id" bigint NULL REFERENCES "crm_estimate" ("id") DEFERRABLE INITIALLY DEFERRED, "lead_id" bigint NULL REFERENCES "crm_lead" ("id") DEFERRABLE INITIALLY DEFERRED, "preferred_gateway_id" bigint NULL REFERENCES "payments_paymentgateway" ("id") DEFERRABLE INITIALLY DEFERRED, "project_id" bigint NULL REFERENCES "projects_project" ("id") DEFERRABLE INITIALLY DEFERRED, "service_id" bigint NULL REFERENCES "services_service" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model PaymentTransaction
--
CREATE TABLE "payments_paymenttransaction" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "uuid" char(32) NOT NULL UNIQUE, "payment_reference" varchar(50) NOT NULL, "customer_name" varchar(150) NOT NULL, "customer_email" varchar(254) NOT NULL, "customer_phone" varchar(30) NOT NULL, "payment_method_type" varchar(40) NOT NULL, "amount" decimal NOT NULL, "tax_amount" decimal NOT NULL, "discount_amount" decimal NOT NULL, "total_amount" decimal NOT NULL, "currency" varchar(10) NOT NULL, "status" varchar(30) NOT NULL, "is_test_mode" bool NOT NULL, "provider_transaction_id" varchar(255) NOT NULL, "provider_order_id" varchar(255) NOT NULL, "payment_response_json" text NOT NULL CHECK ((JSON_VALID("payment_response_json") OR "payment_response_json" IS NULL)), "failure_reason" text NOT NULL, "initiated_at" datetime NOT NULL, "completed_at" datetime NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "gateway_id" bigint NULL REFERENCES "payments_paymentgateway" ("id") DEFERRABLE INITIALLY DEFERRED, "lead_id" bigint NULL REFERENCES "crm_lead" ("id") DEFERRABLE INITIALLY DEFERRED, "payment_method_id" bigint NULL REFERENCES "payments_paymentmethod" ("id") DEFERRABLE INITIALLY DEFERRED, "payment_request_id" bigint NOT NULL REFERENCES "payments_paymentrequest" ("id") DEFERRABLE INITIALLY DEFERRED, "project_id" bigint NULL REFERENCES "projects_project" ("id") DEFERRABLE INITIALLY DEFERRED, "service_id" bigint NULL REFERENCES "services_service" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model PaymentRefund
--
CREATE TABLE "payments_paymentrefund" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "refund_reference" varchar(50) NOT NULL UNIQUE, "requested_amount" decimal NOT NULL, "approved_amount" decimal NOT NULL, "reason" text NOT NULL, "status" varchar(20) NOT NULL, "gateway_refund_id" varchar(255) NOT NULL, "rejection_notes" text NOT NULL, "created_at" datetime NOT NULL, "completed_at" datetime NULL, "approved_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "requested_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "payment_transaction_id" bigint NOT NULL REFERENCES "payments_paymenttransaction" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model PaymentReceipt
--
CREATE TABLE "payments_paymentreceipt" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "receipt_number" varchar(50) NOT NULL UNIQUE, "customer_name" varchar(150) NOT NULL, "customer_email" varchar(254) NOT NULL, "customer_phone" varchar(30) NOT NULL, "customer_address" text NOT NULL, "service_name" varchar(200) NOT NULL, "project_name" varchar(200) NOT NULL, "payment_purpose" varchar(255) NOT NULL, "amount" decimal NOT NULL, "tax_amount" decimal NOT NULL, "total_paid" decimal NOT NULL, "currency" varchar(10) NOT NULL, "payment_method_name" varchar(100) NOT NULL, "gateway_name" varchar(100) NOT NULL, "provider_transaction_id" varchar(255) NOT NULL, "receipt_date" date NOT NULL, "notes" text NOT NULL, "created_at" datetime NOT NULL, "payment_transaction_id" bigint NOT NULL UNIQUE REFERENCES "payments_paymenttransaction" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model PaymentAuditLog
--
CREATE TABLE "payments_paymentauditlog" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "action" varchar(100) NOT NULL, "old_status" varchar(40) NOT NULL, "new_status" varchar(40) NOT NULL, "ip_address" char(39) NULL, "metadata" text NOT NULL CHECK ((JSON_VALID("metadata") OR "metadata" IS NULL)), "created_at" datetime NOT NULL, "user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "payment_request_id" bigint NULL REFERENCES "payments_paymentrequest" ("id") DEFERRABLE INITIALLY DEFERRED, "payment_transaction_id" bigint NULL REFERENCES "payments_paymenttransaction" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model ManualPaymentProof
--
CREATE TABLE "payments_manualpaymentproof" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "payment_reference" varchar(50) NOT NULL, "method" varchar(30) NOT NULL, "bank_reference" varchar(100) NOT NULL, "notes" text NOT NULL, "proof_document" varchar(100) NULL, "status" varchar(20) NOT NULL, "verified_at" datetime NULL, "rejection_reason" text NOT NULL, "created_at" datetime NOT NULL, "verified_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "payment_transaction_id" bigint NOT NULL UNIQUE REFERENCES "payments_paymenttransaction" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model ProjectPaymentMilestone
--
CREATE TABLE "payments_projectpaymentmilestone" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "milestone_name" varchar(150) NOT NULL, "description" text NOT NULL, "percentage" decimal NOT NULL, "amount" decimal NOT NULL, "due_date" date NULL, "status" varchar(20) NOT NULL, "display_order" integer unsigned NOT NULL CHECK ("display_order" >= 0), "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "payment_request_id" bigint NULL REFERENCES "payments_paymentrequest" ("id") DEFERRABLE INITIALLY DEFERRED, "payment_transaction_id" bigint NULL REFERENCES "payments_paymenttransaction" ("id") DEFERRABLE INITIALLY DEFERRED, "project_id" bigint NOT NULL REFERENCES "projects_project" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model ServicePaymentConfiguration
--
CREATE TABLE "payments_servicepaymentconfiguration" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "payment_enabled" bool NOT NULL, "payment_type" varchar(30) NOT NULL, "fixed_amount" decimal NOT NULL, "advance_percentage" decimal NOT NULL, "minimum_amount" decimal NOT NULL, "allow_custom_amount" bool NOT NULL, "consultation_fee" decimal NOT NULL, "site_visit_fee" decimal NOT NULL, "display_payment_button" bool NOT NULL, "gateway_id" bigint NULL REFERENCES "payments_paymentgateway" ("id") DEFERRABLE INITIALLY DEFERRED, "service_id" bigint NOT NULL UNIQUE REFERENCES "services_service" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "payments_paymentmethod_gateway_id_b9343fa1" ON "payments_paymentmethod" ("gateway_id");
CREATE INDEX "payments_paymentrequest_status_fe17984e" ON "payments_paymentrequest" ("status");
CREATE INDEX "payments_paymentrequest_created_by_id_d769dbf7" ON "payments_paymentrequest" ("created_by_id");
CREATE INDEX "payments_paymentrequest_estimate_id_9949f62e" ON "payments_paymentrequest" ("estimate_id");
CREATE INDEX "payments_paymentrequest_lead_id_bfc6e85e" ON "payments_paymentrequest" ("lead_id");
CREATE INDEX "payments_paymentrequest_preferred_gateway_id_abba2219" ON "payments_paymentrequest" ("preferred_gateway_id");
CREATE INDEX "payments_paymentrequest_project_id_4a228ccc" ON "payments_paymentrequest" ("project_id");
CREATE INDEX "payments_paymentrequest_service_id_7f181f4a" ON "payments_paymentrequest" ("service_id");
CREATE INDEX "payments_paymenttransaction_payment_reference_db4f2dfa" ON "payments_paymenttransaction" ("payment_reference");
CREATE INDEX "payments_paymenttransaction_status_54d89342" ON "payments_paymenttransaction" ("status");
CREATE INDEX "payments_paymenttransaction_provider_transaction_id_0e19c63a" ON "payments_paymenttransaction" ("provider_transaction_id");
CREATE INDEX "payments_paymenttransaction_provider_order_id_9f2b9872" ON "payments_paymenttransaction" ("provider_order_id");
CREATE INDEX "payments_paymenttransaction_gateway_id_40645e19" ON "payments_paymenttransaction" ("gateway_id");
CREATE INDEX "payments_paymenttransaction_lead_id_1c74a631" ON "payments_paymenttransaction" ("lead_id");
CREATE INDEX "payments_paymenttransaction_payment_method_id_41debd84" ON "payments_paymenttransaction" ("payment_method_id");
CREATE INDEX "payments_paymenttransaction_payment_request_id_dff9636e" ON "payments_paymenttransaction" ("payment_request_id");
CREATE INDEX "payments_paymenttransaction_project_id_9670b23e" ON "payments_paymenttransaction" ("project_id");
CREATE INDEX "payments_paymenttransaction_service_id_27722503" ON "payments_paymenttransaction" ("service_id");
CREATE INDEX "payments_paymentrefund_status_6a564191" ON "payments_paymentrefund" ("status");
CREATE INDEX "payments_paymentrefund_approved_by_id_39a8744c" ON "payments_paymentrefund" ("approved_by_id");
CREATE INDEX "payments_paymentrefund_requested_by_id_ecdb5926" ON "payments_paymentrefund" ("requested_by_id");
CREATE INDEX "payments_paymentrefund_payment_transaction_id_8a828384" ON "payments_paymentrefund" ("payment_transaction_id");
CREATE INDEX "payments_paymentauditlog_user_id_84b6aac0" ON "payments_paymentauditlog" ("user_id");
CREATE INDEX "payments_paymentauditlog_payment_request_id_6215d337" ON "payments_paymentauditlog" ("payment_request_id");
CREATE INDEX "payments_paymentauditlog_payment_transaction_id_5fb14d2b" ON "payments_paymentauditlog" ("payment_transaction_id");
CREATE INDEX "payments_manualpaymentproof_status_b57d567f" ON "payments_manualpaymentproof" ("status");
CREATE INDEX "payments_manualpaymentproof_verified_by_id_217ef955" ON "payments_manualpaymentproof" ("verified_by_id");
CREATE INDEX "payments_projectpaymentmilestone_payment_request_id_64af964d" ON "payments_projectpaymentmilestone" ("payment_request_id");
CREATE INDEX "payments_projectpaymentmilestone_payment_transaction_id_f197a096" ON "payments_projectpaymentmilestone" ("payment_transaction_id");
CREATE INDEX "payments_projectpaymentmilestone_project_id_ac686712" ON "payments_projectpaymentmilestone" ("project_id");
CREATE INDEX "payments_servicepaymentconfiguration_gateway_id_0e41d75c" ON "payments_servicepaymentconfiguration" ("gateway_id");
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: projects.0002_project_actual_completion_date_and_more
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Add field actual_completion_date to project
--
ALTER TABLE "projects_project" ADD COLUMN "actual_completion_date" date NULL;
--
-- Add field contract_amount to project
--
CREATE TABLE "new__projects_project" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(220) NOT NULL, "slug" varchar(250) NOT NULL UNIQUE, "location" varchar(150) NOT NULL, "project_type" varchar(120) NOT NULL, "client_type" varchar(100) NOT NULL, "project_status" varchar(20) NOT NULL, "duration" varchar(50) NOT NULL, "built_up_area" varchar(50) NOT NULL, "overview" text NOT NULL, "scope_of_work" text NOT NULL, "challenges" text NOT NULL, "solutions" text NOT NULL, "main_image" varchar(100) NULL, "before_image" varchar(100) NULL, "after_image" varchar(100) NULL, "featured" bool NOT NULL, "published" bool NOT NULL, "display_order" integer unsigned NOT NULL CHECK ("display_order" >= 0), "created_at" datetime NOT NULL, "category_id" bigint NOT NULL REFERENCES "projects_projectcategory" ("id") DEFERRABLE INITIALLY DEFERRED, "actual_completion_date" date NULL, "contract_amount" decimal NOT NULL);
INSERT INTO "new__projects_project" ("id", "title", "slug", "location", "project_type", "client_type", "project_status", "duration", "built_up_area", "overview", "scope_of_work", "challenges", "solutions", "main_image", "before_image", "after_image", "featured", "published", "display_order", "created_at", "category_id", "actual_completion_date", "contract_amount") SELECT "id", "title", "slug", "location", "project_type", "client_type", "project_status", "duration", "built_up_area", "overview", "scope_of_work", "challenges", "solutions", "main_image", "before_image", "after_image", "featured", "published", "display_order", "created_at", "category_id", "actual_completion_date", '0' FROM "projects_project";
DROP TABLE "projects_project";
ALTER TABLE "new__projects_project" RENAME TO "projects_project";
CREATE INDEX "projects_project_category_id_708edb98" ON "projects_project" ("category_id");
--
-- Add field customer_email to project
--
CREATE TABLE "new__projects_project" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(220) NOT NULL, "slug" varchar(250) NOT NULL UNIQUE, "location" varchar(150) NOT NULL, "project_type" varchar(120) NOT NULL, "client_type" varchar(100) NOT NULL, "project_status" varchar(20) NOT NULL, "duration" varchar(50) NOT NULL, "built_up_area" varchar(50) NOT NULL, "overview" text NOT NULL, "scope_of_work" text NOT NULL, "challenges" text NOT NULL, "solutions" text NOT NULL, "main_image" varchar(100) NULL, "before_image" varchar(100) NULL, "after_image" varchar(100) NULL, "featured" bool NOT NULL, "published" bool NOT NULL, "display_order" integer unsigned NOT NULL CHECK ("display_order" >= 0), "created_at" datetime NOT NULL, "category_id" bigint NOT NULL REFERENCES "projects_projectcategory" ("id") DEFERRABLE INITIALLY DEFERRED, "actual_completion_date" date NULL, "contract_amount" decimal NOT NULL, "customer_email" varchar(254) NOT NULL);
INSERT INTO "new__projects_project" ("id", "title", "slug", "location", "project_type", "client_type", "project_status", "duration", "built_up_area", "overview", "scope_of_work", "challenges", "solutions", "main_image", "before_image", "after_image", "featured", "published", "display_order", "created_at", "category_id", "actual_completion_date", "contract_amount", "customer_email") SELECT "id", "title", "slug", "location", "project_type", "client_type", "project_status", "duration", "built_up_area", "overview", "scope_of_work", "challenges", "solutions", "main_image", "before_image", "after_image", "featured", "published", "display_order", "created_at", "category_id", "actual_completion_date", "contract_amount", '' FROM "projects_project";
DROP TABLE "projects_project";
ALTER TABLE "new__projects_project" RENAME TO "projects_project";
CREATE INDEX "projects_project_category_id_708edb98" ON "projects_project" ("category_id");
--
-- Add field customer_name to project
--
CREATE TABLE "new__projects_project" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(220) NOT NULL, "slug" varchar(250) NOT NULL UNIQUE, "location" varchar(150) NOT NULL, "project_type" varchar(120) NOT NULL, "client_type" varchar(100) NOT NULL, "project_status" varchar(20) NOT NULL, "duration" varchar(50) NOT NULL, "built_up_area" varchar(50) NOT NULL, "overview" text NOT NULL, "scope_of_work" text NOT NULL, "challenges" text NOT NULL, "solutions" text NOT NULL, "main_image" varchar(100) NULL, "before_image" varchar(100) NULL, "after_image" varchar(100) NULL, "featured" bool NOT NULL, "published" bool NOT NULL, "display_order" integer unsigned NOT NULL CHECK ("display_order" >= 0), "created_at" datetime NOT NULL, "category_id" bigint NOT NULL REFERENCES "projects_projectcategory" ("id") DEFERRABLE INITIALLY DEFERRED, "actual_completion_date" date NULL, "contract_amount" decimal NOT NULL, "customer_email" varchar(254) NOT NULL, "customer_name" varchar(150) NOT NULL);
INSERT INTO "new__projects_project" ("id", "title", "slug", "location", "project_type", "client_type", "project_status", "duration", "built_up_area", "overview", "scope_of_work", "challenges", "solutions", "main_image", "before_image", "after_image", "featured", "published", "display_order", "created_at", "category_id", "actual_completion_date", "contract_amount", "customer_email", "customer_name") SELECT "id", "title", "slug", "location", "project_type", "client_type", "project_status", "duration", "built_up_area", "overview", "scope_of_work", "challenges", "solutions", "main_image", "before_image", "after_image", "featured", "published", "display_order", "created_at", "category_id", "actual_completion_date", "contract_amount", "customer_email", '' FROM "projects_project";
DROP TABLE "projects_project";
ALTER TABLE "new__projects_project" RENAME TO "projects_project";
CREATE INDEX "projects_project_category_id_708edb98" ON "projects_project" ("category_id");
--
-- Add field customer_phone to project
--
CREATE TABLE "new__projects_project" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(220) NOT NULL, "slug" varchar(250) NOT NULL UNIQUE, "location" varchar(150) NOT NULL, "project_type" varchar(120) NOT NULL, "client_type" varchar(100) NOT NULL, "project_status" varchar(20) NOT NULL, "duration" varchar(50) NOT NULL, "built_up_area" varchar(50) NOT NULL, "overview" text NOT NULL, "scope_of_work" text NOT NULL, "challenges" text NOT NULL, "solutions" text NOT NULL, "main_image" varchar(100) NULL, "before_image" varchar(100) NULL, "after_image" varchar(100) NULL, "featured" bool NOT NULL, "published" bool NOT NULL, "display_order" integer unsigned NOT NULL CHECK ("display_order" >= 0), "created_at" datetime NOT NULL, "category_id" bigint NOT NULL REFERENCES "projects_projectcategory" ("id") DEFERRABLE INITIALLY DEFERRED, "actual_completion_date" date NULL, "contract_amount" decimal NOT NULL, "customer_email" varchar(254) NOT NULL, "customer_name" varchar(150) NOT NULL, "customer_phone" varchar(30) NOT NULL);
INSERT INTO "new__projects_project" ("id", "title", "slug", "location", "project_type", "client_type", "project_status", "duration", "built_up_area", "overview", "scope_of_work", "challenges", "solutions", "main_image", "before_image", "after_image", "featured", "published", "display_order", "created_at", "category_id", "actual_completion_date", "contract_amount", "customer_email", "customer_name", "customer_phone") SELECT "id", "title", "slug", "location", "project_type", "client_type", "project_status", "duration", "built_up_area", "overview", "scope_of_work", "challenges", "solutions", "main_image", "before_image", "after_image", "featured", "published", "display_order", "created_at", "category_id", "actual_completion_date", "contract_amount", "customer_email", "customer_name", '' FROM "projects_project";
DROP TABLE "projects_project";
ALTER TABLE "new__projects_project" RENAME TO "projects_project";
CREATE INDEX "projects_project_category_id_708edb98" ON "projects_project" ("category_id");
--
-- Add field customer_user to project
--
ALTER TABLE "projects_project" ADD COLUMN "customer_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
--
-- Add field expected_completion_date to project
--
ALTER TABLE "projects_project" ADD COLUMN "expected_completion_date" date NULL;
--
-- Add field paid_amount to project
--
CREATE TABLE "new__projects_project" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(220) NOT NULL, "slug" varchar(250) NOT NULL UNIQUE, "location" varchar(150) NOT NULL, "project_type" varchar(120) NOT NULL, "client_type" varchar(100) NOT NULL, "project_status" varchar(20) NOT NULL, "duration" varchar(50) NOT NULL, "built_up_area" varchar(50) NOT NULL, "overview" text NOT NULL, "scope_of_work" text NOT NULL, "challenges" text NOT NULL, "solutions" text NOT NULL, "main_image" varchar(100) NULL, "before_image" varchar(100) NULL, "after_image" varchar(100) NULL, "featured" bool NOT NULL, "published" bool NOT NULL, "display_order" integer unsigned NOT NULL CHECK ("display_order" >= 0), "created_at" datetime NOT NULL, "category_id" bigint NOT NULL REFERENCES "projects_projectcategory" ("id") DEFERRABLE INITIALLY DEFERRED, "actual_completion_date" date NULL, "contract_amount" decimal NOT NULL, "customer_email" varchar(254) NOT NULL, "customer_name" varchar(150) NOT NULL, "customer_phone" varchar(30) NOT NULL, "customer_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "expected_completion_date" date NULL, "paid_amount" decimal NOT NULL);
INSERT INTO "new__projects_project" ("id", "title", "slug", "location", "project_type", "client_type", "project_status", "duration", "built_up_area", "overview", "scope_of_work", "challenges", "solutions", "main_image", "before_image", "after_image", "featured", "published", "display_order", "created_at", "category_id", "actual_completion_date", "contract_amount", "customer_email", "customer_name", "customer_phone", "customer_user_id", "expected_completion_date", "paid_amount") SELECT "id", "title", "slug", "location", "project_type", "client_type", "project_status", "duration", "built_up_area", "overview", "scope_of_work", "challenges", "solutions", "main_image", "before_image", "after_image", "featured", "published", "display_order", "created_at", "category_id", "actual_completion_date", "contract_amount", "customer_email", "customer_name", "customer_phone", "customer_user_id", "expected_completion_date", '0' FROM "projects_project";
DROP TABLE "projects_project";
ALTER TABLE "new__projects_project" RENAME TO "projects_project";
CREATE INDEX "projects_project_category_id_708edb98" ON "projects_project" ("category_id");
CREATE INDEX "projects_project_customer_user_id_9909a37d" ON "projects_project" ("customer_user_id");
--
-- Add field progress_percentage to project
--
CREATE TABLE "new__projects_project" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(220) NOT NULL, "slug" varchar(250) NOT NULL UNIQUE, "location" varchar(150) NOT NULL, "project_type" varchar(120) NOT NULL, "client_type" varchar(100) NOT NULL, "project_status" varchar(20) NOT NULL, "duration" varchar(50) NOT NULL, "built_up_area" varchar(50) NOT NULL, "overview" text NOT NULL, "scope_of_work" text NOT NULL, "challenges" text NOT NULL, "solutions" text NOT NULL, "main_image" varchar(100) NULL, "before_image" varchar(100) NULL, "after_image" varchar(100) NULL, "featured" bool NOT NULL, "published" bool NOT NULL, "display_order" integer unsigned NOT NULL CHECK ("display_order" >= 0), "created_at" datetime NOT NULL, "category_id" bigint NOT NULL REFERENCES "projects_projectcategory" ("id") DEFERRABLE INITIALLY DEFERRED, "actual_completion_date" date NULL, "contract_amount" decimal NOT NULL, "customer_email" varchar(254) NOT NULL, "customer_name" varchar(150) NOT NULL, "customer_phone" varchar(30) NOT NULL, "customer_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "expected_completion_date" date NULL, "paid_amount" decimal NOT NULL, "progress_percentage" integer unsigned NOT NULL CHECK ("progress_percentage" >= 0));
INSERT INTO "new__projects_project" ("id", "title", "slug", "location", "project_type", "client_type", "project_status", "duration", "built_up_area", "overview", "scope_of_work", "challenges", "solutions", "main_image", "before_image", "after_image", "featured", "published", "display_order", "created_at", "category_id", "actual_completion_date", "contract_amount", "customer_email", "customer_name", "customer_phone", "customer_user_id", "expected_completion_date", "paid_amount", "progress_percentage") SELECT "id", "title", "slug", "location", "project_type", "client_type", "project_status", "duration", "built_up_area", "overview", "scope_of_work", "challenges", "solutions", "main_image", "before_image", "after_image", "featured", "published", "display_order", "created_at", "category_id", "actual_completion_date", "contract_amount", "customer_email", "customer_name", "customer_phone", "customer_user_id", "expected_completion_date", "paid_amount", 0 FROM "projects_project";
DROP TABLE "projects_project";
ALTER TABLE "new__projects_project" RENAME TO "projects_project";
CREATE INDEX "projects_project_category_id_708edb98" ON "projects_project" ("category_id");
CREATE INDEX "projects_project_customer_user_id_9909a37d" ON "projects_project" ("customer_user_id");
--
-- Add field project_manager to project
--
ALTER TABLE "projects_project" ADD COLUMN "project_manager_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
--
-- Add field start_date to project
--
ALTER TABLE "projects_project" ADD COLUMN "start_date" date NULL;
--
-- Alter field project_status on project
--
CREATE TABLE "new__projects_project" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(220) NOT NULL, "slug" varchar(250) NOT NULL UNIQUE, "location" varchar(150) NOT NULL, "project_type" varchar(120) NOT NULL, "client_type" varchar(100) NOT NULL, "duration" varchar(50) NOT NULL, "built_up_area" varchar(50) NOT NULL, "overview" text NOT NULL, "scope_of_work" text NOT NULL, "challenges" text NOT NULL, "solutions" text NOT NULL, "main_image" varchar(100) NULL, "before_image" varchar(100) NULL, "after_image" varchar(100) NULL, "featured" bool NOT NULL, "published" bool NOT NULL, "display_order" integer unsigned NOT NULL CHECK ("display_order" >= 0), "created_at" datetime NOT NULL, "category_id" bigint NOT NULL REFERENCES "projects_projectcategory" ("id") DEFERRABLE INITIALLY DEFERRED, "actual_completion_date" date NULL, "contract_amount" decimal NOT NULL, "customer_email" varchar(254) NOT NULL, "customer_name" varchar(150) NOT NULL, "customer_phone" varchar(30) NOT NULL, "customer_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "expected_completion_date" date NULL, "paid_amount" decimal NOT NULL, "progress_percentage" integer unsigned NOT NULL CHECK ("progress_percentage" >= 0), "project_manager_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "start_date" date NULL, "project_status" varchar(30) NOT NULL);
INSERT INTO "new__projects_project" ("id", "title", "slug", "location", "project_type", "client_type", "duration", "built_up_area", "overview", "scope_of_work", "challenges", "solutions", "main_image", "before_image", "after_image", "featured", "published", "display_order", "created_at", "category_id", "actual_completion_date", "contract_amount", "customer_email", "customer_name", "customer_phone", "customer_user_id", "expected_completion_date", "paid_amount", "progress_percentage", "project_manager_id", "start_date", "project_status") SELECT "id", "title", "slug", "location", "project_type", "client_type", "duration", "built_up_area", "overview", "scope_of_work", "challenges", "solutions", "main_image", "before_image", "after_image", "featured", "published", "display_order", "created_at", "category_id", "actual_completion_date", "contract_amount", "customer_email", "customer_name", "customer_phone", "customer_user_id", "expected_completion_date", "paid_amount", "progress_percentage", "project_manager_id", "start_date", "project_status" FROM "projects_project";
DROP TABLE "projects_project";
ALTER TABLE "new__projects_project" RENAME TO "projects_project";
CREATE INDEX "projects_project_category_id_708edb98" ON "projects_project" ("category_id");
CREATE INDEX "projects_project_customer_user_id_9909a37d" ON "projects_project" ("customer_user_id");
CREATE INDEX "projects_project_project_manager_id_39466ecc" ON "projects_project" ("project_manager_id");
--
-- Create model ProjectDocument
--
CREATE TABLE "projects_projectdocument" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "document_type" varchar(30) NOT NULL, "title" varchar(200) NOT NULL, "file" varchar(100) NOT NULL, "visibility" varchar(20) NOT NULL, "description" text NOT NULL, "created_at" datetime NOT NULL, "project_id" bigint NOT NULL REFERENCES "projects_project" ("id") DEFERRABLE INITIALLY DEFERRED, "uploaded_by_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model ProjectTask
--
CREATE TABLE "projects_projecttask" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "task_name" varchar(200) NOT NULL, "category" varchar(40) NOT NULL, "start_date" date NULL, "due_date" date NULL, "completed_date" date NULL, "status" varchar(20) NOT NULL, "priority" varchar(10) NOT NULL, "progress_percentage" integer unsigned NOT NULL CHECK ("progress_percentage" >= 0), "notes" text NOT NULL, "display_order" integer unsigned NOT NULL CHECK ("display_order" >= 0), "created_at" datetime NOT NULL, "assigned_to_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "project_id" bigint NOT NULL REFERENCES "projects_project" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model SupportTicket
--
CREATE TABLE "projects_supportticket" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "ticket_id" varchar(40) NOT NULL UNIQUE, "customer_name" varchar(150) NOT NULL, "customer_phone" varchar(30) NOT NULL, "customer_email" varchar(254) NOT NULL, "category" varchar(30) NOT NULL, "priority" varchar(10) NOT NULL, "subject" varchar(255) NOT NULL, "description" text NOT NULL, "status" varchar(25) NOT NULL, "resolution_notes" text NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "assigned_to_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "customer_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "project_id" bigint NULL REFERENCES "projects_project" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model SupportTicketMessage
--
CREATE TABLE "projects_supportticketmessage" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "sender_name" varchar(150) NOT NULL, "message" text NOT NULL, "attachment" varchar(100) NULL, "is_staff_reply" bool NOT NULL, "created_at" datetime NOT NULL, "sender_user_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "ticket_id" bigint NOT NULL REFERENCES "projects_supportticket" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "projects_projectdocument_project_id_41155174" ON "projects_projectdocument" ("project_id");
CREATE INDEX "projects_projectdocument_uploaded_by_id_2e43c47e" ON "projects_projectdocument" ("uploaded_by_id");
CREATE INDEX "projects_projecttask_assigned_to_id_41e5355b" ON "projects_projecttask" ("assigned_to_id");
CREATE INDEX "projects_projecttask_project_id_c579add0" ON "projects_projecttask" ("project_id");
CREATE INDEX "projects_supportticket_status_7f026ada" ON "projects_supportticket" ("status");
CREATE INDEX "projects_supportticket_assigned_to_id_571e8d11" ON "projects_supportticket" ("assigned_to_id");
CREATE INDEX "projects_supportticket_customer_user_id_f10b44ad" ON "projects_supportticket" ("customer_user_id");
CREATE INDEX "projects_supportticket_project_id_219a71fd" ON "projects_supportticket" ("project_id");
CREATE INDEX "projects_supportticketmessage_sender_user_id_4f077604" ON "projects_supportticketmessage" ("sender_user_id");
CREATE INDEX "projects_supportticketmessage_ticket_id_195cd7ac" ON "projects_supportticketmessage" ("ticket_id");
COMMIT;

-- ------------------------------------------------------------------------------
-- Migration: sessions.0001_initial
-- ------------------------------------------------------------------------------
BEGIN;
--
-- Create model Session
--
CREATE TABLE "django_session" ("session_key" varchar(40) NOT NULL PRIMARY KEY, "session_data" text NOT NULL, "expire_date" datetime NOT NULL);
CREATE INDEX "django_session_expire_date_a5c62663" ON "django_session" ("expire_date");
COMMIT;

-- ------------------------------------------------------------------------------
-- RE-ENABLE FOREIGN KEYS
-- ------------------------------------------------------------------------------
SET FOREIGN_KEY_CHECKS = 1;

-- ==============================================================================
-- END OF SCHEMA EXPORT
-- ==============================================================================
