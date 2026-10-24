from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count
from django.views.decorators.http import require_POST
from .models import CodeSource, CodeSourceTopic
from .forms import CodeSourceForm
from django.contrib.auth.models import User


def seed_demo_code_sources():
    """Seed high-quality, topic-wise code sources with GitHub links if database is empty."""
    admin_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
    if not admin_user or CodeSource.objects.exists():
        return

    samples = [
        {
            "title": "Distributed LRU Cache Engine with O(1) Eviction",
            "topic": "Data Structures & Algorithms",
            "language": "python",
            "difficulty": "Intermediate",
            "summary": "High-performance Least Recently Used (LRU) Cache implementation utilizing a doubly linked list and hash map for O(1) get & put operations.",
            "file_name": "lru_cache.py",
            "github_repo_url": "https://github.com/torvalds/linux",
            "tags": "python, dsa, cache, lru, doubly-linked-list, system-design",
            "description": """### Overview
A robust implementation of the classic LRU Cache data structure. Designed to handle thread-safe cache evictions with guaranteed O(1) time complexity for both key lookup and key insertion.

### Architecture
- **Doubly Linked List (`Node`)**: Keeps track of recently used order.
- **Hash Table (`cache`)**: Maps keys directly to nodes for instant O(1) retrieval.
- **Eviction Strategy**: Whenever capacity is reached, the node before the tail (least recently accessed) is removed.

### How to Run
```bash
python lru_cache.py
```""",
            "code_content": """class Node:
    def __init__(self, key: int, value: int):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    \"\"\"Least Recently Used Cache with strict O(1) operations.\"\"\"
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        # Sentinel dummy nodes
        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def _insert_to_front(self, node: Node) -> None:
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._insert_to_front(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self._remove(self.cache[key])
        node = Node(key, value)
        self.cache[key] = node
        self._insert_to_front(node)

        if len(self.cache) > self.capacity:
            lru_node = self.tail.prev
            self._remove(lru_node)
            del self.cache[lru_node.key]


if __name__ == "__main__":
    cache = LRUCache(2)
    cache.put(1, 100)
    cache.put(2, 200)
    print("Key 1:", cache.get(1))  # Returns 100
    cache.put(3, 300)             # Evicts key 2
    print("Key 2 (evicted):", cache.get(2))  # Returns -1
    print("Key 3:", cache.get(3))  # Returns 300
""",
            "is_featured": True,
        },
        {
            "title": "Production JWT Authentication Middleware for FastAPI / Express",
            "topic": "Full-Stack Web Dev",
            "language": "javascript",
            "difficulty": "Intermediate",
            "summary": "Enterprise-ready JSON Web Token (JWT) validation middleware with token rotation, claim inspection, and role-based access control (RBAC).",
            "file_name": "authMiddleware.js",
            "github_repo_url": "https://github.com/expressjs/express",
            "tags": "javascript, express, jwt, authentication, middleware, security",
            "description": """### Overview
Lightweight, secure Node.js Express middleware for validating Bearer tokens in incoming HTTP Authorization headers.

### Features
- Bearer token parsing and secret verification.
- Enforces user roles (Admin vs Student).
- Attaches decoded identity directly onto `req.user`.

### How to Install & Use
```bash
npm install jsonwebtoken
```""",
            "code_content": """const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'codewithamit-super-secret-key-321';

/**
 * Middleware: Verify Bearer JWT
 */
const requireAuth = (req, res, next) => {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({
            error: 'AuthenticationRequired',
            message: 'Authorization Bearer token is missing or malformed.'
        });
    }

    const token = authHeader.split(' ')[1];
    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        req.user = decoded; // { id, username, role, exp }
        next();
    } catch (err) {
        return res.status(403).json({
            error: 'InvalidToken',
            message: 'Token has expired or signature is invalid.'
        });
    }
};

/**
 * Middleware: Enforce Role (e.g. 'admin')
 */
const requireRole = (requiredRole) => {
    return (req, res, next) => {
        if (!req.user || req.user.role !== requiredRole) {
            return res.status(403).json({
                error: 'Forbidden',
                message: `Action requires '${requiredRole}' privileges.`
            });
        }
        next();
    };
};

module.exports = { requireAuth, requireRole };
""",
            "is_featured": True,
        },
        {
            "title": "Django REST Framework Universal Pagination & Dynamic Query Filter",
            "topic": "Django & REST APIs",
            "language": "python",
            "difficulty": "Advanced",
            "summary": "Production standard DRF Custom PageNumberPagination class with configurable page sizes, max limit guards, and optimized metadata response schema.",
            "file_name": "pagination.py",
            "github_repo_url": "https://github.com/encode/django-rest-framework",
            "tags": "python, django, drf, rest-framework, api, backend",
            "description": """### Overview
Eliminates payload overhead by formatting Django querysets with standard API metadata (total records, next link, previous link, and page sizes).

### Usage in DRF Views
Add to `settings.py` or directly inside your `ListAPIView`:
```python
pagination_class = StandardResultsSetPagination
```""",
            "code_content": """from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'meta': {
                'total_records': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'page_size': self.get_page_size(self.request),
                'next_page_url': self.get_next_link(),
                'previous_page_url': self.get_previous_link(),
            },
            'results': data
        })
""",
            "is_featured": False,
        },
        {
            "title": "React Reusable useDebounce Custom Hook for Live Search Inputs",
            "topic": "React & Modern Frontend",
            "language": "typescript",
            "difficulty": "Beginner",
            "summary": "TypeScript custom hook that delays updating values until user stops typing for N milliseconds, drastically reducing API calls.",
            "file_name": "useDebounce.ts",
            "github_repo_url": "https://github.com/facebook/react",
            "tags": "react, typescript, hooks, frontend, performance, search",
            "description": """### Overview
A clean custom hook to throttle rapid changes such as keystrokes in search input fields.

### Example Usage
```tsx
const [query, setQuery] = useState('');
const debouncedQuery = useDebounce(query, 300);

useEffect(() => {
    fetchResults(debouncedQuery);
}, [debouncedQuery]);
```""",
            "code_content": """import { useState, useEffect } from 'react';

/**
 * useDebounce Hook
 * @param value The value to debounce (e.g. search term)
 * @param delay Milliseconds to wait before updating
 */
export function useDebounce<T>(value: T, delay: number = 300): T {
    const [debouncedValue, setDebouncedValue] = useState<T>(value);

    useEffect(() => {
        const handler = setTimeout(() => {
            setDebouncedValue(value);
        }, delay);

        return () => {
            clearTimeout(handler);
        };
    }, [value, delay]);

    return debouncedValue;
}
""",
            "is_featured": True,
        },
        {
            "title": "Optimized PostgreSQL Schema for E-Commerce Orders with ACID Constraints",
            "topic": "Databases & SQL Queries",
            "language": "sql",
            "difficulty": "Intermediate",
            "summary": "Robust SQL schema with indexes, foreign key cascade behaviors, check constraints for positive prices, and automated updated_at triggers.",
            "file_name": "ecommerce_schema.sql",
            "github_repo_url": "https://github.com/postgres/postgres",
            "tags": "sql, postgresql, database, schema, indexes, ecommerce",
            "description": """### Overview
Enterprise schema for relational order and catalog management. Includes indexed lookup on user IDs and order timestamps.""",
            "code_content": """-- ===================================================
-- CODEWITHAMIT: E-COMMERCE CORE ORDER SCHEMA
-- ===================================================

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    total_amount NUMERIC(10, 2) NOT NULL CHECK (total_amount >= 0),
    status VARCHAR(30) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PAID', 'SHIPPED', 'CANCELLED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for high-volume customer queries
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
""",
            "is_featured": False,
        }
    ]

    for item in samples:
        CodeSource.objects.create(
            author=admin_user,
            **item
        )


def code_source_list(request):
    """Browse, filter, and search topic-wise code sources with GitHub repo links."""
    # Ensure seed samples exist
    if not CodeSource.objects.exists():
        seed_demo_code_sources()

    queryset = CodeSource.objects.filter(is_published=True).select_related('author')

    # Query params
    selected_topic = request.GET.get('topic', '').strip()
    selected_lang = request.GET.get('lang', '').strip()
    selected_difficulty = request.GET.get('difficulty', '').strip()
    query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'latest')

    if selected_topic:
        queryset = queryset.filter(topic=selected_topic)

    if selected_lang:
        queryset = queryset.filter(language=selected_lang.lower())

    if selected_difficulty:
        queryset = queryset.filter(difficulty=selected_difficulty)

    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query) |
            Q(code_content__icontains=query)
        )

    # Sorting
    if sort_by == 'popular':
        queryset = queryset.order_by('-views_count', '-created_at')
    elif sort_by == 'copies':
        queryset = queryset.order_by('-copies_count', '-created_at')
    else:
        queryset = queryset.order_by('-is_featured', '-created_at')

    # Distinct topics and language list with counts
    all_topics = (
        CodeSource.objects.filter(is_published=True)
        .values('topic')
        .annotate(count=Count('id'))
        .order_by('topic')
    )

    all_languages = (
        CodeSource.objects.filter(is_published=True)
        .values('language')
        .annotate(count=Count('id'))
        .order_by('language')
    )

    is_admin = (
        request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.is_superuser or 
            getattr(getattr(request.user, 'profile', None), 'role', '') == 'admin'
        )
    )

    return render(request, 'code_sources/code_source_list.html', {
        'code_sources': queryset,
        'selected_topic': selected_topic,
        'selected_lang': selected_lang,
        'selected_difficulty': selected_difficulty,
        'query': query,
        'sort_by': sort_by,
        'all_topics': all_topics,
        'all_languages': all_languages,
        'total_count': CodeSource.objects.filter(is_published=True).count(),
        'is_admin': is_admin,
    })


def code_source_detail(request, slug):
    """View detailed code with copy, download, and direct GitHub repo access."""
    code_source = get_object_or_404(
        CodeSource.objects.select_related('author'),
        slug=slug
    )

    # Increment view counter
    code_source.views_count += 1
    code_source.save(update_fields=['views_count'])

    # Related items in same topic
    related_sources = (
        CodeSource.objects.filter(is_published=True, topic=code_source.topic)
        .exclude(id=code_source.id)[:4]
    )

    is_admin = (
        request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.is_superuser or 
            getattr(getattr(request.user, 'profile', None), 'role', '') == 'admin' or
            request.user == code_source.author
        )
    )

    return render(request, 'code_sources/code_source_detail.html', {
        'code_source': code_source,
        'related_sources': related_sources,
        'is_admin': is_admin,
    })


@login_required
def add_code_source(request):
    """Admin/Staff view to publish a new code source with GitHub repo link."""
    is_admin = (
        request.user.is_staff or 
        request.user.is_superuser or 
        getattr(getattr(request.user, 'profile', None), 'role', '') == 'admin'
    )
    if not is_admin:
        messages.error(request, "Permission denied. Only Administrators can publish code sources.")
        return redirect('code_sources:list')

    if request.method == 'POST':
        form = CodeSourceForm(request.POST)
        if form.is_valid():
            code_source = form.save(commit=False)
            code_source.author = request.user
            code_source.save()
            messages.success(request, f"✨ Code source '{code_source.title}' and GitHub repository link successfully published!")
            return redirect('code_sources:detail', slug=code_source.slug)
    else:
        # Prepopulate with topic if provided in query param
        initial_topic = request.GET.get('topic', '')
        form = CodeSourceForm(initial={'topic': initial_topic} if initial_topic else None)

    return render(request, 'code_sources/code_source_form.html', {
        'form': form,
        'is_edit': False,
    })


@login_required
def edit_code_source(request, slug):
    """Edit existing code source and repository link."""
    code_source = get_object_or_404(CodeSource, slug=slug)
    is_admin = (
        request.user.is_staff or 
        request.user.is_superuser or 
        getattr(getattr(request.user, 'profile', None), 'role', '') == 'admin' or
        request.user == code_source.author
    )
    if not is_admin:
        messages.error(request, "Permission denied to edit this code resource.")
        return redirect('code_sources:detail', slug=code_source.slug)

    if request.method == 'POST':
        form = CodeSourceForm(request.POST, instance=code_source)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Updated '{code_source.title}' successfully!")
            return redirect('code_sources:detail', slug=code_source.slug)
    else:
        form = CodeSourceForm(instance=code_source)

    return render(request, 'code_sources/code_source_form.html', {
        'form': form,
        'code_source': code_source,
        'is_edit': True,
    })


@login_required
def delete_code_source(request, slug):
    """Delete a code source."""
    code_source = get_object_or_404(CodeSource, slug=slug)
    is_admin = (
        request.user.is_staff or 
        request.user.is_superuser or 
        getattr(getattr(request.user, 'profile', None), 'role', '') == 'admin'
    )
    if not is_admin:
        messages.error(request, "Permission denied to delete this resource.")
        return redirect('code_sources:detail', slug=code_source.slug)

    if request.method == 'POST':
        title = code_source.title
        code_source.delete()
        messages.success(request, f"🗑️ Code source '{title}' was deleted.")
        return redirect('code_sources:list')

    return render(request, 'code_sources/confirm_delete.html', {'code_source': code_source})


def download_code(request, slug):
    """Download raw code file directly."""
    code_source = get_object_or_404(CodeSource, slug=slug)
    filename = code_source.file_name or f"{code_source.slug}.txt"
    response = HttpResponse(code_source.code_content, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@require_POST
def copy_code_api(request, pk):
    """AJAX endpoint when user clicks 'Copy Code'."""
    try:
        code_source = CodeSource.objects.get(pk=pk)
        code_source.copies_count += 1
        code_source.save(update_fields=['copies_count'])
        return JsonResponse({'success': True, 'copies_count': code_source.copies_count})
    except CodeSource.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not found'}, status=404)
