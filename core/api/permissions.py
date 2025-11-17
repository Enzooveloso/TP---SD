from rest_framework.permissions import BasePermission, SAFE_METHODS
from core.models import Monografia, Banca


class IsAlunoOwnerOrOrientador(BasePermission):
    """
    Permite alterações para admin, autor (aluno), orientador ou coorientador.
    """

    def has_object_permission(self, request, view, obj: Monografia):
        user = request.user
        if user.is_staff or user.is_superuser:
            return True
        if hasattr(user, "aluno_profile") and obj.aluno == user.aluno_profile:
            return True
        if hasattr(user, "professor_profile"):
            prof = user.professor_profile
            return obj.orientador == prof or obj.coorientador == prof
        return request.method in SAFE_METHODS


class IsProfessorOrAdminBanca(BasePermission):
    """
    Restringe a gestão da banca a admins, orientadores ou coorientadores.
    """

    def has_object_permission(self, request, view, obj: Banca):
        user = request.user
        if user.is_staff or user.is_superuser:
            return True
        if not hasattr(user, "professor_profile"):
            return False
        prof = user.professor_profile
        monografia = obj.monografia
        return monografia.orientador == prof or monografia.coorientador == prof
