# -*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Count, Min, Sum, Max, Avg
from minimo.cliente.models import *
from minimo.documento.utils import *
from minimo.template.models import *
from django.core.urlresolvers import reverse
from minimo.tassa.models import *
from datetime import datetime, timedelta
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

import os




class Conto(models.Model):
    nome = models.CharField('Nome conto', max_length=70)
    numeto = models.CharField('Numero conto', max_length=70)
    saldo = importo = models.FloatField('Saldo', default=0)
    data_ultimo_aggiornamento = models.DateField('Data ultimo aggiornamento', auto_now=True)
    
    class Meta:
        verbose_name = 'Conto'
        verbose_name_plural='Conti'
        ordering=['nome']
        
TIPO = (
        ('E', 'Entrata'),
        ('U', 'Uscita'),
    )    
class Movimento(models.Model):
    user = models.ForeignKey(User, editable=False)
    conto = models.ForeignKey('Conto', null=True, blank=True)
    tipo = models.CharField('Tipo movimento', max_length=70, choices=TIPO)
    data_movimento = models.DateField('Data movimnto', null=True, blank=True)
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField( null=True, blank=True)
    documento = generic.GenericForeignKey('content_type', 'object_id')
    descrizione = models.TextField('Descrizione', max_length=1024, null=True, blank=True)
    importo = models.FloatField('Importo')

    class Meta:
        verbose_name = 'Movimento'
        verbose_name_plural='Movimenti'
        ordering=['data_movimento']

    def __unicode__(self):
        return "%s - %s %s" %(self.tipo, self.descrizione, self.importo)
    
    def get_documento(self):
        return self.documento
    
    def save(self, *args, **kwargs):
        conto = Conto.objects.all()[0]
        self.conto = conto
        if self.tipo == 'E':
            conto.saldo += self.importo
        if self.tipo == 'U':
            conto.saldo -= self.importo
        conto.save()
        super(Movimento, self).save(*args, **kwargs)
        

TIPO_FATTURA = (
    ('F', 'Fornitore'),
    ('S', 'Servizi'),
)



class FattureFornitore(models.Model):
    
    def attachment_upload(instance, filename):
    
        print 'wow ', 'attachments/%s/%s/%s' % (
                '%s_%s' % (instance._meta.app_label,
                           instance._meta.object_name.lower()),
                           instance.content_object.pk,
                           filename)
        return 'attachments/%s/%s/%s' % (
                '%s_%s' % (instance._meta.app_label,
                           instance._meta.object_name.lower()),
                           instance.content_object.pk,
                           filename)

    user = models.ForeignKey(User, editable=False)
    tipo = models.CharField('Tipo fattura', max_length=70, choices=TIPO_FATTURA)
    data_documento = models.DateField('Data Emissione documento', null=True, blank=True)
    numero = models.CharField('Numero documento', max_length=70)
    scadenza_pagamento = models.DateField('Data scadenza documento', null=True, blank=True)
    descrizione = models.TextField('Descrizione', max_length=1024, null=True, blank=True)
    importo = models.FloatField('Importo')
    #stato = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Fatture Fornitore'
        verbose_name_plural='Fatture Fornitore'
        ordering=['data_documento']

    def __unicode__(self):
        return "%s %s" %(self.tipo,  self.importo)
    

class ContoOption(admin.ModelAdmin):
    pass

admin.site.register(Conto, ContoOption)