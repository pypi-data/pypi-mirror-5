# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'InfographicBox.channel_name'
        db.add_column(u'infographics_infographicbox', 'channel_name',
                      self.gf('django.db.models.fields.CharField')(max_length=140, null=True, db_index=True),
                      keep_default=False)

        # Adding field 'InfographicBox.channel_long_slug'
        db.add_column(u'infographics_infographicbox', 'channel_long_slug',
                      self.gf('django.db.models.fields.CharField')(max_length=250, null=True, db_index=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'InfographicBox.channel_name'
        db.delete_column(u'infographics_infographicbox', 'channel_name')

        # Deleting field 'InfographicBox.channel_long_slug'
        db.delete_column(u'infographics_infographicbox', 'channel_long_slug')


    models = {
        "%s.%s" % (User._meta.app_label, User._meta.module_name): {
        'Meta': {'object_name': User.__name__},
        },
        u'articles.album': {
            'Meta': {'ordering': "['-date_available']", 'object_name': 'Album', '_ormbases': [u'articles.Article']},
            u'article_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['articles.Article']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'articles.article': {
            'Meta': {'ordering': "['-date_available']", 'object_name': 'Article'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['channels.Channel']"}),
            'channel_long_slug': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'db_index': 'True'}),
            'channel_name': ('django.db.models.fields.CharField', [], {'max_length': '140', 'null': 'True', 'db_index': 'True'}),
            'child_class': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'db_index': 'True'}),
            'date_available': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'hat': ('django.db.models.fields.CharField', [], {'max_length': '140', 'null': 'True', 'blank': 'True'}),
            'headline': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'article_images'", 'to': u"orm['images.Image']", 'through': u"orm['articles.ArticleImage']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'main_image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['images.Image']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '140', 'null': 'True'}),
            'short_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'}),
            'sources': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['sources.Source']", 'null': 'True', 'through': u"orm['articles.ArticleSource']", 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '140', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['%s.%s']" % (User._meta.app_label, User._meta.object_name)})

        },
        u'articles.articleimage': {
            'Meta': {'object_name': 'ArticleImage'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'articleimage_articles'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['articles.Article']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['images.Image']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'articles.articlesource': {
            'Meta': {'object_name': 'ArticleSource'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'articlesource_articles'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['articles.Article']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'articlesource_sources'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['sources.Source']"})
        },
        u'articles.post': {
            'Meta': {'ordering': "['-date_available']", 'object_name': 'Post', '_ormbases': [u'articles.Article']},
            'albums': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'post_albums'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['articles.Album']"}),
            u'article_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['articles.Article']", 'unique': 'True', 'primary_key': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'channels.channel': {
            'Meta': {'object_name': 'Channel'},
            'date_available': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'homepage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'long_slug': ('django.db.models.fields.SlugField', [], {'max_length': '250'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'subchannel'", 'null': 'True', 'to': u"orm['channels.Channel']"}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'show_in_menu': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['%s.%s']" % (User._meta.app_label, User._meta.object_name)})

        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'images.image': {
            'Meta': {'object_name': 'Image'},
            'date_available': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '150', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sources.Source']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '140', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['%s.%s']" % (User._meta.app_label, User._meta.object_name)})

        },
        u'infographics.infographic': {
            'Meta': {'ordering': "['order']", 'object_name': 'Infographic'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['channels.Channel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'css_path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_available': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'headline': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'infographic_item'", 'to': u"orm['infographics.InfographicItem']", 'through': u"orm['infographics.InfographicInfographicItem']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'js_path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'main_image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'infographic_image'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['images.Image']"}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'posts': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'infographic_post'", 'to': u"orm['articles.Post']", 'through': u"orm['infographics.InfographicPost']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'}),
            'timeline': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'infographic_timeline'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['timelinejs.Timeline']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'top_image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'infographic_topimage'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['images.Image']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'gallery'", 'max_length': '20'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['%s.%s']" % (User._meta.app_label, User._meta.object_name)})

        },
        u'infographics.infographicbox': {
            'Meta': {'object_name': 'InfographicBox'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['articles.Article']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['channels.Channel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'channel_long_slug': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'db_index': 'True'}),
            'channel_name': ('django.db.models.fields.CharField', [], {'max_length': '140', 'null': 'True', 'db_index': 'True'}),
            'date_available': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'infographics': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'infographicbox_infographics'", 'to': u"orm['infographics.Infographic']", 'through': u"orm['infographics.InfographicBoxInfographics']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '140'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['%s.%s']" % (User._meta.app_label, User._meta.object_name)})

        },
        u'infographics.infographicboxinfographics': {
            'Meta': {'object_name': 'InfographicBoxInfographics'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'infographic': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'infographicboxinfographics_infographics'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['infographics.Infographic']"}),
            'infographicbox': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'infographicboxinfographics_infographicboxes'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['infographics.InfographicBox']"}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'infographics.infographicconfig': {
            'Meta': {'unique_together': "(('key_group', 'key', 'site', 'channel', 'article', 'infographic'),)", 'object_name': 'InfographicConfig'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['articles.Article']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['channels.Channel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'date_available': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'format': ('django.db.models.fields.CharField', [], {'default': "'text'", 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'infographic': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'infographicconfig_infographics'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['infographics.Infographic']"}),
            'key': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '150'}),
            'key_group': ('django.db.models.fields.SlugField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['sites.Site']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['%s.%s']" % (User._meta.app_label, User._meta.object_name)})
,
            'value': ('django.db.models.fields.TextField', [], {})
        },
        u'infographics.infographicinfographicitem': {
            'Meta': {'object_name': 'InfographicInfographicItem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'infographic': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'infographicitem_infographic'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['infographics.Infographic']"}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'infographicitem_item'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['infographics.InfographicItem']"})
        },
        u'infographics.infographicitem': {
            'Meta': {'object_name': 'InfographicItem'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'infographicitem_album'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['articles.Album']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['images.Image']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '150'}),
            'timeline': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'infographicitem_timeline'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['timelinejs.Timeline']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'infographics.infographicpost': {
            'Meta': {'object_name': 'InfographicPost'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'infographic': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'infographicpost_infographic'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['infographics.Infographic']"}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'infographicpost_post'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['articles.Post']"})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'sources.source': {
            'Meta': {'object_name': 'Source'},
            'date_available': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'feed': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '140'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['%s.%s']" % (User._meta.app_label, User._meta.object_name)})

        },
        u'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_tagged_items'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_items'", 'to': u"orm['taggit.Tag']"})
        },
        u'timelinejs.timeline': {
            'Meta': {'object_name': 'Timeline'},
            'asset_caption': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'asset_credit': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'asset_media': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['channels.Channel']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'headline': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'posts': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'timeline_post'", 'to': u"orm['articles.Post']", 'through': u"orm['timelinejs.TimelinePost']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'source': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '50'})
        },
        u'timelinejs.timelinepost': {
            'Meta': {'object_name': 'TimelinePost'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'timelinepost_post'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['articles.Post']"}),
            'timeline': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'timelinepost_timeline'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['timelinejs.Timeline']"})
        }
    }

    complete_apps = ['infographics']