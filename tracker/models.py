from django.db import models
from django.utils import timezone

class Project(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    path = models.CharField(max_length=500, blank=True)
    language = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=7, default='#00d4aa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ['-updated_at']
    def __str__(self): return self.name
    @property
    def total_seconds(self): return sum(s.useful_seconds for s in self.sessions.filter(ended_at__isnull=False))
    @property
    def total_sessions(self): return self.sessions.filter(ended_at__isnull=False).count()

class Session(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sessions')
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    auto_closed = models.BooleanField(default=False)
    class Meta: ordering = ['-started_at']
    def __str__(self): return f"{self.project.name} — {self.started_at.strftime('%Y-%m-%d %H:%M')}"
    @property
    def is_active(self): return self.ended_at is None
    @property
    def total_seconds(self):
        if not self.ended_at: return int((timezone.now()-self.started_at).total_seconds())
        return int((self.ended_at-self.started_at).total_seconds())
    @property
    def coding_seconds(self):
        total=0; events=list(self.events.order_by('timestamp')); in_test=False; last_time=self.started_at
        for e in events:
            if e.event_type=='server_start': total+=int((e.timestamp-last_time).total_seconds()); in_test=True; last_time=e.timestamp
            elif e.event_type=='server_stop': in_test=False; last_time=e.timestamp
            elif e.event_type=='session_end':
                if not in_test: total+=int((e.timestamp-last_time).total_seconds())
        if not events: return self.total_seconds
        return total
    @property
    def testing_seconds(self):
        total=0; events=list(self.events.order_by('timestamp')); last_time=None
        for e in events:
            if e.event_type=='server_start': last_time=e.timestamp
            elif e.event_type=='server_stop' and last_time: total+=int((e.timestamp-last_time).total_seconds()); last_time=None
        return total
    @property
    def useful_seconds(self): return self.coding_seconds+self.testing_seconds

class Event(models.Model):
    EVENT_TYPES = [('session_start','Session Start'),('session_end','Session End'),('server_start','Server Start'),('server_stop','Server Stop')]
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    timestamp = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)
    class Meta: ordering = ['timestamp']
    def __str__(self): return f"{self.event_type} @ {self.timestamp.strftime('%H:%M:%S')}"
