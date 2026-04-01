from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from accounts.new import CookieJWTAuthentication2

from .models import Domain, DomainMembership
from .serializers import DomainSerializer, DomainMembershipSerializer
from .permissions import IsAnyDomainManager, IsDomainManager, is_any_domain_manager


class DomainListView(APIView):
    """
    GET  /api/domains/   -> list all active domains (public)
    POST /api/domains/   -> create a new domain (managers only)
    """
    authentication_classes = [CookieJWTAuthentication2]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAnyDomainManager()]
        return [AllowAny()]

    def get(self, request):
        domains = Domain.objects.filter(is_active=True)
        serializer = DomainSerializer(domains, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        serializer = DomainSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DomainDetailView(APIView):
    """
    GET    /api/domains/<slug>/   -> domain detail + caller's membership info
    PATCH  /api/domains/<slug>/   -> edit domain (managers only)
    DELETE /api/domains/<slug>/   -> soft-delete domain (managers only)
    """
    authentication_classes = [CookieJWTAuthentication2]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [IsAuthenticated(), IsDomainManager()]
        return [AllowAny()]

    def _get_domain(self, slug):
        try:
            return Domain.objects.get(slug=slug)
        except Domain.DoesNotExist:
            return None

    def get(self, request, slug):
        domain = self._get_domain(slug)
        if not domain:
            return Response({"error": "Domain not found."}, status=status.HTTP_404_NOT_FOUND)

        data = DomainSerializer(domain, context={"request": request}).data

        # Attach caller's memberships in this domain
        if request.user and request.user.is_authenticated:
            memberships = DomainMembership.objects.filter(
                user=request.user, domain=domain, is_approved=True
            )
            data["my_roles"] = [m.role for m in memberships]
        else:
            data["my_roles"] = []

        return Response(data)

    def patch(self, request, slug):
        domain = self._get_domain(slug)
        if not domain:
            return Response({"error": "Domain not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DomainSerializer(domain, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        domain = self._get_domain(slug)
        if not domain:
            return Response({"error": "Domain not found."}, status=status.HTTP_404_NOT_FOUND)

        domain.is_active = False
        domain.save()
        return Response({"message": f"Domain '{slug}' deactivated."})


class DomainMembersView(APIView):
    """
    GET    /api/domains/<slug>/members/        -> list all memberships for domain
    POST   /api/domains/<slug>/members/        -> apply for / add membership
    """
    authentication_classes = [CookieJWTAuthentication2]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated(), IsDomainManager()]
        return [IsAuthenticated()]

    def _get_domain(self, slug):
        try:
            return Domain.objects.get(slug=slug, is_active=True)
        except Domain.DoesNotExist:
            return None

    def get(self, request, slug):
        domain = self._get_domain(slug)
        if not domain:
            return Response({"error": "Domain not found."}, status=status.HTTP_404_NOT_FOUND)

        memberships = DomainMembership.objects.filter(domain=domain)
        serializer = DomainMembershipSerializer(memberships, many=True)
        return Response(serializer.data)

    def post(self, request, slug):
        """
        Apply to a domain.
        - mentee: auto-approved (if mentee_reg_open or requester is manager)
        - mentor: requires approval (if mentor_reg_open or requester is manager), is_approved=False
        - manager can bypass reg restrictions and add anyone
        """
        domain = self._get_domain(slug)
        if not domain:
            return Response({"error": "Domain not found."}, status=status.HTTP_404_NOT_FOUND)

        role = request.data.get("role")
        if role not in ("mentor", "mentee", "manager"):
            return Response({"error": "Invalid role."}, status=status.HTTP_400_BAD_REQUEST)

        # Only a domain manager can grant manager role
        if role == "manager" and not is_any_domain_manager(request.user):
            return Response({"error": "Only managers can grant manager role."}, status=status.HTTP_403_FORBIDDEN)

        # Enforce registration-open settings (managers bypass)
        caller_is_manager = is_any_domain_manager(request.user)
        if role == "mentee" and not domain.mentee_reg_open and not caller_is_manager:
            return Response({"error": "Mentee registration is currently closed for this domain."}, status=status.HTTP_403_FORBIDDEN)
        if role == "mentor" and not domain.mentor_reg_open and not caller_is_manager:
            return Response({"error": "Mentor registration is currently closed for this domain."}, status=status.HTTP_403_FORBIDDEN)

        # Mentees and managers are auto-approved; mentors need approval
        auto_approve = role in ("mentee", "manager")

        membership, created = DomainMembership.objects.get_or_create(
            user=request.user,
            domain=domain,
            role=role,
            defaults={"is_approved": auto_approve},
        )

        if not created:
            return Response(
                {"error": f"You already have a '{role}' membership in this domain."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Auto-create Mentor / Mentee profile rows so portal pages work immediately
        try:
            from accounts.models import UserProfile
            from projects.models import Mentor, Mentee
            user_profile = UserProfile.objects.get(user=request.user)
            if role == "mentee":
                Mentee.objects.get_or_create(user=user_profile, domain=domain)
            elif role == "mentor":
                Mentor.objects.get_or_create(user=user_profile, domain=domain)
        except Exception:
            pass  # Don't fail the membership creation if profile creation fails

        serializer = DomainMembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class DomainMemberDetailView(APIView):
    """
    PATCH  /api/domains/<slug>/members/<membership_id>/  -> approve membership
    DELETE /api/domains/<slug>/members/<membership_id>/  -> remove membership
    """
    authentication_classes = [CookieJWTAuthentication2]
    permission_classes = [IsAuthenticated, IsDomainManager]

    def _get_membership(self, membership_id, slug):
        try:
            return DomainMembership.objects.get(id=membership_id, domain__slug=slug)
        except DomainMembership.DoesNotExist:
            return None

    def patch(self, request, slug, membership_id):
        membership = self._get_membership(membership_id, slug)
        if not membership:
            return Response({"error": "Membership not found."}, status=status.HTTP_404_NOT_FOUND)

        membership.is_approved = True
        membership.save()
        serializer = DomainMembershipSerializer(membership)
        return Response(serializer.data)

    def delete(self, request, slug, membership_id):
        membership = self._get_membership(membership_id, slug)
        if not membership:
            return Response({"error": "Membership not found."}, status=status.HTTP_404_NOT_FOUND)

        membership.delete()
        return Response({"message": "Membership removed."})


class AllDomainsForManagerView(APIView):
    """
    GET /api/domains/all/  -> list ALL domains (including inactive) for manager dashboard
    """
    authentication_classes = [CookieJWTAuthentication2]
    permission_classes = [IsAuthenticated, IsAnyDomainManager]

    def get(self, request):
        domains = Domain.objects.all()
        serializer = DomainSerializer(domains, many=True, context={"request": request})
        return Response(serializer.data)
