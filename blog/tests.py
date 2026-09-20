from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from blog.models import BlogCategory, BlogPost
from blog.forms import BlogPostForm, BlogCategoryForm

class BlogModelTests(TestCase):
    def setUp(self):
        self.category = BlogCategory.objects.create(
            name="Flat Renovation Test",
            description="Testing category"
        )

    def test_category_slug_auto_generation(self):
        self.assertEqual(self.category.slug, "flat-renovation-test")

    def test_blog_post_slug_and_reading_time(self):
        post = BlogPost.objects.create(
            title="Complete 3BHK Flat Renovation Checklist",
            category=self.category,
            short_description="A short test description",
            content="<p>" + "word " * 400 + "</p>",  # 400 words = ~2 min read
            status="draft"
        )
        self.assertEqual(post.slug, "complete-3bhk-flat-renovation-checklist")
        self.assertEqual(post.reading_time, 2)
        self.assertFalse(post.is_published)

    def test_publish_auto_date(self):
        post = BlogPost.objects.create(
            title="Publish Date Auto Assignment Test",
            category=self.category,
            short_description="Short desc",
            content="Content here",
            status="published"
        )
        self.assertIsNotNone(post.published_date)
        self.assertTrue(post.is_published)


class PublicBlogViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat1 = BlogCategory.objects.create(name="Construction", slug="construction")
        self.cat2 = BlogCategory.objects.create(name="Renovation", slug="renovation")

        # Create 1 published and 1 draft post in cat1
        self.pub_post1 = BlogPost.objects.create(
            title="Published Home Building Guide",
            slug="published-home-building-guide",
            category=self.cat1,
            short_description="Published guide",
            content="Building homes with quality RCC",
            status="published",
            published_date=timezone.now()
        )
        self.draft_post1 = BlogPost.objects.create(
            title="Draft Internal Document",
            slug="draft-internal-document",
            category=self.cat1,
            short_description="Draft post",
            content="Secret draft content",
            status="draft"
        )

        # Create 1 published in cat2
        self.pub_post2 = BlogPost.objects.create(
            title="Published Flat Remodeling Tips",
            slug="published-flat-remodeling-tips",
            category=self.cat2,
            short_description="Renovation tips",
            content="Waterproofing and flooring tips",
            status="published",
            published_date=timezone.now()
        )

    def test_public_list_shows_only_published_posts(self):
        response = self.client.get(reverse('blog:public_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Published Home Building Guide")
        self.assertContains(response, "Published Flat Remodeling Tips")
        self.assertNotContains(response, "Draft Internal Document")

    def test_public_list_category_filter(self):
        response = self.client.get(reverse('blog:public_list') + '?category=construction')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Published Home Building Guide")
        self.assertNotContains(response, "Published Flat Remodeling Tips")

    def test_public_list_search(self):
        response = self.client.get(reverse('blog:public_list') + '?q=Waterproofing')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Published Flat Remodeling Tips")
        self.assertNotContains(response, "Published Home Building Guide")

    def test_public_detail_published_post_success(self):
        response = self.client.get(reverse('blog:public_detail', kwargs={'slug': self.pub_post1.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.pub_post1.title)

    def test_public_detail_draft_post_returns_404(self):
        response = self.client.get(reverse('blog:public_detail', kwargs={'slug': self.draft_post1.slug}))
        self.assertEqual(response.status_code, 404)


class CMSBlogSecurityAndCRUDTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='cms_admin',
            password='securepassword123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regular_visitor',
            password='securepassword123',
            is_staff=False
        )
        self.category = BlogCategory.objects.create(name="Demolition Services", slug="demolition-services")
        self.blog = BlogPost.objects.create(
            title="Safe Building Demolition Protocol",
            slug="safe-building-demolition-protocol",
            category=self.category,
            short_description="Safe razing methods",
            content="Safety first in demolition",
            status="draft"
        )

    def test_anonymous_user_blocked_from_cms(self):
        response = self.client.get(reverse('blog:cms_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/cms/login/', response.url)

    def test_regular_non_staff_user_blocked_from_cms(self):
        self.client.login(username='regular_visitor', password='securepassword123')
        response = self.client.get(reverse('blog:cms_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/cms/login/', response.url)

    def test_staff_user_can_access_cms_dashboard_and_list(self):
        self.client.login(username='cms_admin', password='securepassword123')
        
        response_dash = self.client.get(reverse('blog:cms_dashboard'))
        self.assertEqual(response_dash.status_code, 200)
        self.assertContains(response_dash, "Blog Management Dashboard")

        response_list = self.client.get(reverse('blog:cms_list'))
        self.assertEqual(response_list.status_code, 200)
        self.assertContains(response_list, "Safe Building Demolition Protocol")

    def test_toggle_publish_status(self):
        self.client.login(username='cms_admin', password='securepassword123')
        self.assertEqual(self.blog.status, 'draft')

        # Publish via POST
        response = self.client.post(reverse('blog:cms_toggle_publish', kwargs={'pk': self.blog.pk}))
        self.assertEqual(response.status_code, 302)
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.status, 'published')
        self.assertIsNotNone(self.blog.published_date)

        # Unpublish via POST
        response = self.client.post(reverse('blog:cms_toggle_publish', kwargs={'pk': self.blog.pk}))
        self.assertEqual(response.status_code, 302)
        self.blog.refresh_from_db()
        self.assertEqual(self.blog.status, 'draft')

    def test_delete_blog_post_post_only(self):
        self.client.login(username='cms_admin', password='securepassword123')
        blog_pk = self.blog.pk

        # GET request renders confirmation page
        response_get = self.client.get(reverse('blog:cms_delete', kwargs={'pk': blog_pk}))
        self.assertEqual(response_get.status_code, 200)
        self.assertContains(response_get, "Confirm Permanent Deletion")
        self.assertTrue(BlogPost.objects.filter(pk=blog_pk).exists())

        # POST request executes deletion
        response_post = self.client.post(reverse('blog:cms_delete', kwargs={'pk': blog_pk}))
        self.assertEqual(response_post.status_code, 302)
        self.assertFalse(BlogPost.objects.filter(pk=blog_pk).exists())

    def test_safe_category_deletion_protection(self):
        self.client.login(username='cms_admin', password='securepassword123')
        
        # Category contains self.blog, so POST delete should fail and not delete category
        response = self.client.post(reverse('blog:cms_category_delete', kwargs={'pk': self.category.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(BlogCategory.objects.filter(pk=self.category.pk).exists())

        # Delete the blog first
        self.blog.delete()

        # Now category deletion should succeed
        response = self.client.post(reverse('blog:cms_category_delete', kwargs={'pk': self.category.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(BlogCategory.objects.filter(pk=self.category.pk).exists())

    def test_ai_assist_endpoint(self):
        self.client.login(username='cms_admin', password='securepassword123')
        response = self.client.post(
            reverse('blog:cms_ai_assist'),
            data={
                'topic': 'How to inspect old flats before renovation',
                'task_type': 'generate_draft'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIn('content', data)

    def test_clone_blog_post(self):
        self.client.login(username='cms_admin', password='securepassword123')
        response = self.client.post(reverse('blog:cms_clone', kwargs={'pk': self.blog.pk}))
        self.assertEqual(response.status_code, 302)
        cloned = BlogPost.objects.filter(title__startswith='Copy of ').first()
        self.assertIsNotNone(cloned)
        self.assertEqual(cloned.status, 'draft')
        self.assertEqual(cloned.category, self.blog.category)
