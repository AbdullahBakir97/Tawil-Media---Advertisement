from datetime import datetime
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import ValidationError
from typing import List, Optional, Dict, Any

def archive_content(content_obj, archive_reason: str = None) -> None:
    """
    Archive a content object (Article or Magazine) by marking it as archived
    and recording the archive date and reason.
    """
    if not hasattr(content_obj, 'is_archived'):
        raise ValidationError("Object does not support archiving")
    
    content_obj.is_archived = True
    content_obj.archived_at = timezone.now()
    content_obj.archive_reason = archive_reason
    content_obj.save()

def restore_from_archive(content_obj) -> None:
    """
    Restore a content object from archive status.
    """
    if not hasattr(content_obj, 'is_archived'):
        raise ValidationError("Object does not support archiving")
    
    content_obj.is_archived = False
    content_obj.archived_at = None
    content_obj.archive_reason = None
    content_obj.save()

def get_archive_stats(model_class, start_date: Optional[datetime] = None, 
                     end_date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Get statistics about archived content within a date range.
    """
    query = Q(is_archived=True)
    if start_date:
        query &= Q(archived_at__gte=start_date)
    if end_date:
        query &= Q(archived_at__lte=end_date)
    
    total_archived = model_class.objects.filter(query).count()
    recently_archived = model_class.objects.filter(
        is_archived=True,
        archived_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).count()
    
    return {
        'total_archived': total_archived,
        'recently_archived': recently_archived,
        'archive_rate': recently_archived / 30 if recently_archived > 0 else 0
    }

def bulk_archive(objects: List[Any], archive_reason: str = None) -> int:
    """
    Archive multiple content objects at once.
    Returns the number of successfully archived objects.
    """
    count = 0
    for obj in objects:
        try:
            archive_content(obj, archive_reason)
            count += 1
        except ValidationError:
            continue
    return count
