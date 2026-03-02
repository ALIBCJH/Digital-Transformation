# Recursive Hierarchical Organization - Architecture Documentation

## 🎯 Overview

This redesign implements a **scalable, recursive tree structure** for managing a global religious organization, starting with a Central Region demo that can expand infinitely without schema changes.

---

## 🌳 The Recursive Schema

### Core Innovation: Single `OrganizationNode` Model

Instead of separate tables for Region, Sub-Region, Country, etc., we use **one self-referential table**:

```python
class OrganizationNode(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    parent = models.ForeignKey('self', ...)  # Self-referential!
    path = models.CharField(max_length=1000)  # Materialized Path
    depth = models.IntegerField()
```

**Benefits:**
- ✅ Infinite nesting without schema changes
- ✅ Add new levels (Continent, District, Zone) without migrations
- ✅ Same code works for any depth
- ✅ O(1) ancestor/descendant queries

---

## 🚀 Postgres Optimization: Materialized Path Pattern

### The Problem
Traditional recursive queries (`WITH RECURSIVE`) are slow: **O(n log n)** or worse.

### The Solution: Materialized Path
Each node stores its **full path from root**:

```
Root:         /GLOBAL/
Continent:    /GLOBAL/AFRICA/
Country:      /GLOBAL/AFRICA/KENYA/
Region:       /GLOBAL/AFRICA/KENYA/CENTRAL/
Sub-Region:   /GLOBAL/AFRICA/KENYA/CENTRAL/NYERI/
```

### Query Performance

**Find all descendants (O(1)):**
```sql
SELECT * FROM organization_nodes 
WHERE path LIKE '/GLOBAL/AFRICA/KENYA/CENTRAL/%';
```
**Index used:** `BTREE(path)` or `GIN(path)` for pattern matching

**Find all ancestors (O(1)):**
```python
# Extract parent paths from materialized path
# /GLOBAL/AFRICA/KENYA/ → [/GLOBAL/, /GLOBAL/AFRICA/]
path_parts = node.path.strip('/').split('/')
ancestor_paths = ['/' + '/'.join(path_parts[:i+1]) + '/' 
                  for i in range(len(path_parts) - 1)]

# Single query
OrganizationNode.objects.filter(path__in=ancestor_paths)
```

### Indexing Strategy

```python
class Meta:
    indexes = [
        models.Index(fields=['path']),           # BTREE for exact match
        models.Index(fields=['parent', 'is_active']),
        models.Index(fields=['depth', 'is_active']),
        GinIndex(fields=['path'], opclasses=['gin_trgm_ops']),  # For LIKE queries
    ]
```

**Why GIN Index?**
- Optimizes `path LIKE '/GLOBAL/AFRICA/%'` queries
- Reduces scan time from O(n) to **O(log n)**
- Requires Postgres extension: `CREATE EXTENSION pg_trgm;`

---

## 🔒 Multi-Tenant Filtering

### User Scope Model

Each admin has an `admin_scope` pointing to a node:

```python
class User(AbstractUser):
    admin_scope = models.ForeignKey(
        OrganizationNode,
        help_text='Node this user manages'
    )
```

### Automatic Filtering

```python
def get_accessible_nodes(self):
    """Returns scope + all descendants (O(1) query)"""
    if self.is_superuser:
        return OrganizationNode.objects.filter(is_active=True)
    
    if not self.admin_scope:
        return OrganizationNode.objects.none()
    
    # Path-based filtering (single query!)
    return OrganizationNode.objects.filter(
        path__startswith=self.admin_scope.path,
        is_active=True
    )
```

### Example: Nyeri Admin
- `admin_scope` = Nyeri Sub-Region (`/CENTRAL/NYERI/`)
- Accessible nodes: Nyeri + 2 altars
- **Single query:** `WHERE path LIKE '/CENTRAL/NYERI/%'`

### Example: Central Admin
- `admin_scope` = Central Region (`/CENTRAL/`)
- Accessible nodes: Central + 6 sub-regions + 7 altars
- **Single query:** `WHERE path LIKE '/CENTRAL/%'`

---

## 📊 Standardized API Response

### The Contract

**Every hierarchy endpoint returns this structure:**

```json
{
  "current": {
    "id": 5,
    "code": "NYERI",
    "name": "Nyeri",
    "depth": 2,
    "path": "/CENTRAL/NYERI/"
  },
  "parent": {
    "id": 1,
    "code": "CENTRAL",
    "name": "Central Region",
    "depth": 1
  },
  "children": [
    {
      "id": 10,
      "code": "NYERI_MAIN",
      "name": "Nyeri Main Altar",
      "total_members": 450
    },
    {
      "id": 11,
      "code": "NYERI_GATITO",
      "name": "Gatito Altar",
      "total_members": 320
    }
  ],
  "breadcrumb": [
    {"code": "GLOBAL", "name": "Global Organization", "depth": 0},
    {"code": "CENTRAL", "name": "Central Region", "depth": 1}
  ],
  "stats": {
    "total_altars": 2,
    "total_members": 770,
    "direct_children": 2
  },
  "user_scope": {
    "can_edit": true,
    "admin_scope": "CENTRAL",
    "is_superuser": false
  }
}
```

### Frontend Benefits

**Same React component works at ANY level:**

```javascript
// Works for Region, Sub-Region, or Altar
function HierarchyView({ nodeId }) {
  const { data } = useFetch(`/api/nodes/${nodeId}/`);
  
  return (
    <div>
      <Breadcrumb trail={data.breadcrumb} />
      <NodeHeader node={data.current} stats={data.stats} />
      <ChildrenList children={data.children} />
      {data.parent && <BackButton parent={data.parent} />}
    </div>
  );
}
```

---

## 🏗️ Central Region Demo Structure

```
/CENTRAL/ (Central Region - Root for demo)
├── /CENTRAL/NYERI/ (Nyeri Sub-Region)
│   ├── /CENTRAL/NYERI/NYERI_MAIN/ (Nyeri Main Altar)
│   └── /CENTRAL/NYERI/NYERI_GATITO/ (Gatito Altar)
├── /CENTRAL/MWEIGA/ (Mweiga Sub-Region)
│   └── /CENTRAL/MWEIGA/MWEIGA_001/ (Mweiga Altar)
├── /CENTRAL/KARATINA/ (Karatina Sub-Region)
│   └── /CENTRAL/KARATINA/KARATINA_001/ (Karatina Altar)
├── /CENTRAL/CHAKA/ (Chaka Sub-Region)
│   └── /CENTRAL/CHAKA/CHAKA_001/ (Chaka Altar)
├── /CENTRAL/MUKURWEINI/ (MUKURWE-INI Sub-Region)
│   └── /CENTRAL/MUKURWEINI/MUKURWEINI_001/ (Mukurwe-ini Altar)
└── /CENTRAL/KIENI/ (Kieni Sub-Region)
    └── /CENTRAL/KIENI/KIENI_001/ (Kieni Altar)
```

**Expansion Path (Future):**
```
/GLOBAL/
└── /GLOBAL/AFRICA/
    └── /GLOBAL/AFRICA/KENYA/
        └── /GLOBAL/AFRICA/KENYA/CENTRAL/
            └── /GLOBAL/AFRICA/KENYA/CENTRAL/NYERI/
                └── /GLOBAL/AFRICA/KENYA/CENTRAL/NYERI/NYERI_MAIN/
```

---

## ⚡ Performance Characteristics

| Operation | Traditional | Materialized Path |
|-----------|------------|-------------------|
| Get Children | O(n) | O(log n) with index |
| Get Ancestors | O(n) recursive | O(1) with path index |
| Get Descendants | O(n²) | O(log n) with LIKE |
| Check if Ancestor | O(n) | O(1) string check |
| Move Subtree | O(n²) | O(n) path update |

### Database Indexes Created

1. **BTREE(path)** - Exact path lookups
2. **GIN(path)** - Pattern matching (`LIKE` queries)
3. **BTREE(parent, is_active)** - Children queries
4. **BTREE(depth, is_active)** - Level-based queries

---

## 🚀 Migration from Old Schema

### Step 1: Create New Tables
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Seed Central Region
```bash
python manage.py seed_central_region
```

### Step 3: Migrate Existing Data (if any)
```python
# Map old Altar model to new structure
for old_altar in OldAltar.objects.all():
    parent_node = OrganizationNode.objects.get(code=old_altar.region_code)
    Altar.objects.create(
        code=old_altar.code,
        name=old_altar.name,
        parent_node=parent_node,
        ...
    )
```

---

## 📝 Usage Examples

### Create New Sub-Region
```python
from core.models_redesign import OrganizationNode

central = OrganizationNode.objects.get(code='CENTRAL')

new_sub_region = OrganizationNode.objects.create(
    code='NANYUKI',
    name='Nanyuki',
    parent=central
)
# Auto-generates: path="/CENTRAL/NANYUKI/", depth=2
```

### Query User's Scope
```python
# Get all nodes Nyeri admin can see
nyeri_admin = User.objects.get(username='nyeri_admin')
accessible = nyeri_admin.get_accessible_nodes()
# Returns: Nyeri + 2 child altars (via path filtering)
```

### Check Permissions
```python
node = OrganizationNode.objects.get(code='NYERI_MAIN')
if user.can_manage_node(node):
    # User can edit this node
    node.name = "Updated Name"
    node.save()
```

---

## 🎯 Summary

This redesign achieves:

✅ **Infinite scalability** - Add 100 levels without schema changes  
✅ **O(1) queries** - Materialized path + indexes  
✅ **Multi-tenant isolation** - Path-based filtering  
✅ **Standardized API** - Same JSON structure everywhere  
✅ **Demo-ready** - Central Region seeded and working  
✅ **Future-proof** - Expand to global without refactoring  

**Key Innovation:** By storing the full path (`/GLOBAL/AFRICA/KENYA/CENTRAL/NYERI/`), we transform expensive tree operations into simple string prefix matching, leveraging Postgres's optimized indexing.
