from django.conf import settings
from django.db import models
from .conf import options
from .compat import get_user_model

user_model = get_user_model()


class AccessToken(models.Model):
    user = models.ForeignKey(user_model, related_name="access_tokens")
    client = models.ForeignKey("Client", related_name="access_tokens")
    
    refresh_token = models.ForeignKey("RefreshToken", related_name="access_tokens")
    token = models.CharField(max_length=100)
    scope = models.ManyToManyField("Scope", related_name="access_tokens")
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.token
    
    def generate_token(self):
        from .compat import get_random_string
        
        return get_random_string(100)
    
    def revoke(self):
        self.is_active = False
        self.save()
        
    def save(self, *args, **kwargs):
        from .compat import now
        import datetime
        
        if not self.token:
            self.token = self.generate_token()
        
        self.expires_at = now() + options.access_token["expires"]
        
        super(AccessToken, self).save(*args, **kwargs)


class AuthorizationCode(models.Model):
    client = models.ForeignKey("Client", related_name="authorization_codes")
    scope = models.ManyToManyField("Scope", related_name="authorization_codes")
    redirect_uri = models.ForeignKey("RedirectUri", related_name="authorization_codes")
    
    token = models.CharField(max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.token
    
    def generate_token(self):
        from .compat import get_random_string
        
        return get_random_string(100)
        
    def save(self, *args, **kwargs):
        from .compat import now
        import datetime
        
        if not self.token:
            self.token = self.generate_token()
        
        self.expires_at = now() + options.auth_code["expires"]
        
        super(AuthorizationCode, self).save(*args, **kwargs)


class AuthorizationToken(models.Model):
    user = models.ForeignKey(user_model, related_name="authorization_tokens")
    client = models.ForeignKey("Client", related_name="authorization_tokens")
    token = models.CharField(max_length=100)
    scope = models.ManyToManyField("Scope", related_name="authorization_tokens")
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.token
    
    def generate_refresh_token(self):
        if self.is_active:
            try:
                temp = self.refresh_token
                
                return None
            except RefreshToken.DoesNotExist:
                self.refresh_token = RefreshToken()
                
                self.refresh_token.client = self.client
                self.refresh_token.user = self.user
                self.refresh_token.save()
                
                self.refresh_token.scope = self.scope.all()
                self.refresh_token.save()
                
                self.is_active = False
                self.save()
                
                return self.refresh_token
            
        return None
    
    def generate_token(self):
        from .compat import get_random_string
        
        return get_random_string(100)
    
    def revoke_tokens(self):
        self.is_active = False
        self.save()
        
        self.refresh_token.revoke_tokens()
        
    def save(self, *args, **kwargs):
        from .compat import now
        import datetime
        
        if not self.token:
            self.token = self.generate_token()
        
        self.expires_at = now() + options.auth_token["expires"]
        
        super(AuthorizationToken, self).save(*args, **kwargs)


class Client(models.Model):
    name = models.CharField(max_length=255)
    secret = models.CharField(max_length=50)
    access_host = models.URLField(max_length=255)
    is_active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.name
    
    def generate_secret(self):
        from .compat import get_random_string
        
        return get_random_string(50)
        
    def save(self, *args, **kwargs):
        self.secret = self.generate_secret()
        
        super(Client, self).save(*args, **kwargs)


class RedirectUri(models.Model):
    client = models.ForeignKey("Client", related_name="redirect_uris")
    url = models.URLField(max_length=255)
    
    class Meta:
        verbose_name = "redirect URI"
    
    def __unicode__(self):
        return self.url


class RefreshToken(models.Model):
    user = models.ForeignKey(user_model, related_name="refresh_tokens")
    client = models.ForeignKey("Client", related_name="refresh_tokens")
    
    authorization_token = models.OneToOneField("AuthorizationToken", related_name="refresh_token")
    token = models.CharField(max_length=100)
    scope = models.ManyToManyField("Scope", related_name="refresh_tokens")
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return self.token
    
    def generate_access_token(self):
        access_token = AccessToken(client=self.client, user=self.user, refresh_token=self)
        access_token.save()
        
        access_token.scope = self.scope.all()
        access_token.save()
        
        return access_token
    
    def generate_token(self):
        from .compat import get_random_string
        
        return get_random_string(100)
    
    def revoke_tokens(self):
        self.is_active = False
        self.save()
        
        for access_token in self.access_tokens.all():
            access_token.revoke()
    
    def save(self, *args, **kwargs):
        from .compat import now
        import datetime
        
        if not self.token:
            self.token = self.generate_token()
        
        self.expires_at = now() + options.refresh_token["expires"]
        
        super(RefreshToken, self).save(*args, **kwargs)


class Scope(models.Model):
    short_name = models.CharField(max_length=40)
    full_name = models.CharField(max_length=255)
    description = models.TextField()
