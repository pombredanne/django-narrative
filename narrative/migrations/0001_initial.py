# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Event'
        db.create_table('narrative_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('event_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('event_operand', self.gf('django.db.models.fields.CharField')(default=False, max_length=64, blank=True)),
            ('event_operand_detail', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
            ('Issue_id', self.gf('django.db.models.fields.CharField')(max_length=36, blank=True)),
        ))
        db.send_create_signal('narrative', ['Event'])

        # Adding model 'Solution'
        db.create_table('narrative_solution', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('Issue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['narrative.Issue'])),
            ('diagnostic_Issue_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('problem_description', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('plan_json', self.gf('django.db.models.fields.TextField')()),
            ('enacted', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('narrative', ['Solution'])

        # Adding model 'AssertionMeta'
        db.create_table('narrative_assertionmeta', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('assertion_load_path', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('narrative', ['AssertionMeta'])

        # Adding model 'Issue'
        db.create_table('narrative_issue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('failed_assertion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['narrative.AssertionMeta'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('created_timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('resolved_timestamp', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('narrative', ['Issue'])

        # Adding model 'IssueComment'
        db.create_table('narrative_issuecomment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['narrative.Issue'])),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('narrative', ['IssueComment'])


    def backwards(self, orm):
        # Deleting model 'Event'
        db.delete_table('narrative_event')

        # Deleting model 'Solution'
        db.delete_table('narrative_solution')

        # Deleting model 'AssertionMeta'
        db.delete_table('narrative_assertionmeta')

        # Deleting model 'Issue'
        db.delete_table('narrative_issue')

        # Deleting model 'IssueComment'
        db.delete_table('narrative_issuecomment')


    models = {
        'narrative.assertionmeta': {
            'Meta': {'object_name': 'AssertionMeta'},
            'assertion_load_path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'display_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'narrative.event': {
            'Issue_id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'Meta': {'object_name': 'Event'},
            'event_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'event_operand': ('django.db.models.fields.CharField', [], {'default': 'False', 'max_length': '64', 'blank': 'True'}),
            'event_operand_detail': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'status': ('django.db.models.fields.IntegerField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'narrative.issue': {
            'Meta': {'object_name': 'Issue'},
            'created_timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'failed_assertion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['narrative.AssertionMeta']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resolved_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'narrative.issuecomment': {
            'Meta': {'object_name': 'IssueComment'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['narrative.Issue']"})
        },
        'narrative.solution': {
            'Issue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['narrative.Issue']"}),
            'Meta': {'object_name': 'Solution'},
            'diagnostic_Issue_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'enacted': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plan_json': ('django.db.models.fields.TextField', [], {}),
            'problem_description': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['narrative']