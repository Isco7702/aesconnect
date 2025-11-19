from marshmallow import Schema, fields, validate, validates_schema, ValidationError

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)
    full_name = fields.Str(required=True, validate=validate.Length(min=3))
    bio = fields.Str(validate=validate.Length(max=500))
    avatar_url = fields.Url()
    country = fields.Str()
    city = fields.Str()
    created_at = fields.DateTime(dump_only=True)

class UserRegisterSchema(UserSchema):
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))
    
    class Meta:
        fields = ('username', 'email', 'password', 'full_name', 'country', 'city', 'avatar_url')

class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class PostSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    content = fields.Str(required=True, validate=validate.Length(max=1000))
    image_url = fields.Url(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    likes_count = fields.Int(dump_only=True)
    comments_count = fields.Int(dump_only=True)
    
    # Pour l'affichage dans le feed
    username = fields.Str(dump_only=True)
    full_name = fields.Str(dump_only=True)
    avatar_url = fields.Url(dump_only=True)
    user_liked = fields.Bool(dump_only=True)

class PostCreateSchema(Schema):
    content = fields.Str(required=True, validate=validate.Length(max=1000))
    # Note: image_file est géré via request.files, non via un schéma JSON

class CommentSchema(Schema):
    id = fields.Int(dump_only=True)
    post_id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    content = fields.Str(required=True, validate=validate.Length(max=500))
    created_at = fields.DateTime(dump_only=True)
    
    # Pour l'affichage
    username = fields.Str(dump_only=True)
    full_name = fields.Str(dump_only=True)
    avatar_url = fields.Url(dump_only=True)

class CommentCreateSchema(Schema):
    content = fields.Str(required=True, validate=validate.Length(max=500))

class LikeSchema(Schema):
    id = fields.Int(dump_only=True)
    post_id = fields.Int(required=True)
    user_id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class SuccessSchema(Schema):
    success = fields.Bool(required=True)
    message = fields.Str(required=True)


class GroupSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=3))
    description = fields.Str(validate=validate.Length(max=500))
    creator_id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    is_private = fields.Bool()
    members_count = fields.Int(dump_only=True)
    
    # Pour l'affichage
    creator_username = fields.Str(dump_only=True)

class GroupCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3))
    description = fields.Str(validate=validate.Length(max=500))
    is_private = fields.Bool()

class GroupMemberSchema(Schema):
    group_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    joined_at = fields.DateTime(dump_only=True)
    is_admin = fields.Bool(dump_only=True)

class MessageSchema(Schema):
    id = fields.Int(dump_only=True)
    sender_id = fields.Int(dump_only=True)
    receiver_id = fields.Int(dump_only=True)
    content = fields.Str(required=True, validate=validate.Length(max=1000))
    created_at = fields.DateTime(dump_only=True)
    is_read = fields.Bool(dump_only=True)
    
    # Pour l'affichage
    sender_username = fields.Str(dump_only=True)
    receiver_username = fields.Str(dump_only=True)

class MessageSendSchema(Schema):
    receiver_id = fields.Int(required=True)
    content = fields.Str(required=True, validate=validate.Length(max=1000))

class NotificationSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    message = fields.Str(dump_only=True)
    is_read = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    entity_type = fields.Str(dump_only=True)
    entity_id = fields.Int(dump_only=True)

class ReportSchema(Schema):
    id = fields.Int(dump_only=True)
    reporter_id = fields.Int(dump_only=True)
    reported_user_id = fields.Int(allow_none=True)
    reported_post_id = fields.Int(allow_none=True)
    reason = fields.Str(required=True, validate=validate.Length(max=500))
    status = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class ReportCreateSchema(Schema):
    reported_user_id = fields.Int(allow_none=True)
    reported_post_id = fields.Int(allow_none=True)
    reason = fields.Str(required=True, validate=validate.Length(max=500))
    
    @validates_schema
    def validate_report_target(self, data, **kwargs):
        if not data.get('reported_user_id') and not data.get('reported_post_id'):
            raise ValidationError('Vous devez signaler un utilisateur ou un post.')
