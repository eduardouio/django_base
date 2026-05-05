from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class CustomUserForm(forms.ModelForm):
    """Formulario para editar perfil de usuario (sin cambio de contraseña)"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'picture', 'notes']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Ingrese su nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Ingrese su apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Ingrese su correo electrónico'
            }),
            'picture': forms.FileInput(attrs={
                'class': 'file-input file-input-bordered w-full',
                'accept': 'image/*'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'placeholder': 'Notas adicionales (opcional)',
                'rows': 4
            }),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'picture': 'Foto de Perfil',
            'notes': 'Notas',
        }
        help_texts = {
            'email': 'Este correo será usado para iniciar sesión.',
            'picture': 'Formatos soportados: JPG, PNG, GIF. Tamaño máximo: 5MB.',
            'notes': 'Información adicional sobre el usuario.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que el email sea obligatorio
        self.fields['email'].required = True

    def clean_email(self):
        """Validar que el email no esté siendo usado por otro usuario"""
        email = self.cleaned_data.get('email')
        if email:
            # Verificar si otro usuario ya tiene este email
            existing_user = User.objects.filter(
                email=email).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise ValidationError(
                    'Este correo electrónico ya está siendo utilizado por otro usuario.')
        return email

    def clean_picture(self):
        """Validar el archivo de imagen"""
        picture = self.cleaned_data.get('picture')
        if picture:
            # Validar tamaño (5MB máximo)
            if picture.size > 5 * 1024 * 1024:
                raise ValidationError(
                    'El archivo es demasiado grande. El tamaño máximo es 5MB.')

            # Validar tipo de archivo
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            if not any(picture.name.lower().endswith(ext) for ext in valid_extensions):
                raise ValidationError(
                    'Formato de archivo no válido. Use JPG, PNG o GIF.')

        return picture
