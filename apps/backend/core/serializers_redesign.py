"""
STANDARDIZED API SERIALIZERS FOR HIERARCHICAL ORGANIZATION
==========================================================

Provides consistent JSON structure:
{
    "current": {...},
    "parent": {...},
    "children": [...],
    "breadcrumb": [...],
    "stats": {...}
}
"""

from rest_framework import serializers
from .models_redesign import OrganizationNode, Altar, User, Member


class NodeBreadcrumbSerializer(serializers.ModelSerializer):
    """Minimal node info for breadcrumb trails"""
    class Meta:
        model = OrganizationNode
        fields = ['id', 'code', 'name', 'depth']


class NodeMinimalSerializer(serializers.ModelSerializer):
    """Lightweight node representation for parent/children"""
    class Meta:
        model = OrganizationNode
        fields = ['id', 'code', 'name', 'depth', 'total_altars', 'total_members']


class AltarMinimalSerializer(serializers.ModelSerializer):
    """Lightweight altar representation"""
    class Meta:
        model = Altar
        fields = ['id', 'code', 'name', 'member_count', 'city']


class NodeDetailSerializer(serializers.ModelSerializer):
    """
    Full node details with parent, children, and breadcrumb.
    This is the STANDARD response format for all hierarchy views.
    """

    # Related entities
    parent = NodeMinimalSerializer(read_only=True)
    children = serializers.SerializerMethodField()
    altars = AltarMinimalSerializer(many=True, read_only=True)

    # Navigation
    breadcrumb = serializers.SerializerMethodField()

    # Statistics
    stats = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationNode
        fields = [
            'id', 'code', 'name', 'depth', 'path',
            'parent', 'children', 'altars',
            'breadcrumb', 'stats',
            'is_active', 'created_at'
        ]

    def get_children(self, obj):
        """Get direct children nodes"""
        children = obj.get_children()
        return NodeMinimalSerializer(children, many=True).data

    def get_breadcrumb(self, obj):
        """Get ancestor trail for navigation"""
        ancestors = obj.get_ancestors()
        return NodeBreadcrumbSerializer(ancestors, many=True).data

    def get_stats(self, obj):
        """Aggregate statistics for this node"""
        return {
            'total_altars': obj.total_altars,
            'total_members': obj.total_members,
            'direct_children': obj.children.filter(is_active=True).count(),
            'depth': obj.depth
        }


class AltarDetailSerializer(serializers.ModelSerializer):
    """Full altar details with organizational context"""

    parent_node = NodeMinimalSerializer(read_only=True)
    breadcrumb = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()

    class Meta:
        model = Altar
        fields = [
            'id', 'code', 'name', 'address', 'city',
            'latitude', 'longitude',
            'parent_node', 'breadcrumb', 'stats',
            'established_date', 'is_active'
        ]

    def get_breadcrumb(self, obj):
        """Get organizational path to this altar"""
        ancestors = obj.parent_node.get_ancestors()
        breadcrumb = NodeBreadcrumbSerializer(ancestors, many=True).data
        # Add parent node
        breadcrumb.append(NodeBreadcrumbSerializer(obj.parent_node).data)
        return breadcrumb

    def get_stats(self, obj):
        """Altar statistics"""
        return {
            'member_count': obj.member_count,
            'capacity': obj.capacity,
            'attendance_rate': round((obj.member_count / obj.capacity * 100), 1) if obj.capacity else None
        }


class MemberListSerializer(serializers.ModelSerializer):
    """Member list with altar context"""
    altar_name = serializers.CharField(source='home_altar.name', read_only=True)
    altar_code = serializers.CharField(source='home_altar.code', read_only=True)

    class Meta:
        model = Member
        fields = [
            'id', 'full_name', 'phone_number', 'email',
            'gender', 'membership_date',
            'altar_name', 'altar_code', 'is_active'
        ]


# ============================================
# STANDARDIZED API RESPONSE WRAPPER
# ============================================

def create_hierarchy_response(node, user=None):
    """
    Factory function to create standardized hierarchy response.

    Returns:
    {
        "current": {node details},
        "parent": {parent details or null},
        "children": [{child1}, {child2}, ...],
        "breadcrumb": [{root}, {level1}, {level2}, ...],
        "stats": {aggregated statistics},
        "user_scope": {user's access level}
    }
    """

    response = {
        "current": {
            "id": node.id,
            "code": node.code,
            "name": node.name,
            "depth": node.depth,
            "path": node.path,
        },
        "parent": None,
        "children": [],
        "altars": [],
        "breadcrumb": [],
        "stats": {
            "total_altars": node.total_altars,
            "total_members": node.total_members,
            "direct_children": 0,
        }
    }

    # Parent
    if node.parent:
        response["parent"] = {
            "id": node.parent.id,
            "code": node.parent.code,
            "name": node.parent.name,
            "depth": node.parent.depth,
        }

    # Children
    children = node.get_children()
    response["children"] = [
        {
            "id": child.id,
            "code": child.code,
            "name": child.name,
            "depth": child.depth,
            "total_altars": child.total_altars,
            "total_members": child.total_members,
        }
        for child in children
    ]
    response["stats"]["direct_children"] = len(response["children"])

    # Altars (leaf nodes)
    altars = node.altars.filter(is_active=True)
    response["altars"] = [
        {
            "id": altar.id,
            "code": altar.code,
            "name": altar.name,
            "member_count": altar.member_count,
            "city": altar.city,
        }
        for altar in altars
    ]

    # Breadcrumb
    ancestors = node.get_ancestors()
    response["breadcrumb"] = [
        {
            "id": ancestor.id,
            "code": ancestor.code,
            "name": ancestor.name,
            "depth": ancestor.depth,
        }
        for ancestor in ancestors
    ]

    # User scope (if authenticated)
    if user and user.is_authenticated:
        response["user_scope"] = {
            "can_edit": user.can_manage_node(node),
            "admin_scope": user.admin_scope.code if user.admin_scope else None,
            "is_superuser": user.is_superuser,
        }

    return response
