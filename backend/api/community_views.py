from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from .models import CommunityDiscussion, CommunityReply, NewsletterSubscriber, SiteFeedback
# Removed logging import - using print statements for debugging

@api_view(['GET'])
@permission_classes([AllowAny])
def community_stats(request):
    """Get community statistics"""

    try:
        active_members = NewsletterSubscriber.objects.filter(is_active=True).count()
        success_stories = SiteFeedback.objects.filter(feedback_type='general').count()
        total_discussions = CommunityDiscussion.objects.count()
        

        
        # Calculate success rate (placeholder logic)
        success_rate = round((success_stories / max(active_members, 1)) * 100) if active_members > 0 else 0
        
        response_data = {
            'active_members': active_members,
            'success_stories': success_stories,
            'success_rate': min(success_rate, 100),  # Cap at 100%
            'total_discussions': total_discussions
        }
        

        return Response(response_data)
    except Exception as e:

        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def topic_stats(request):
    """Get statistics for each topic"""

    try:
        topics = CommunityDiscussion.TOPIC_CHOICES
        topic_stats = {}
        
        for topic_id, topic_name in topics:
            discussions_count = CommunityDiscussion.objects.filter(topic=topic_id).count()
            replies_count = CommunityReply.objects.filter(discussion__topic=topic_id).count()
            total_discussions = discussions_count + replies_count  # Questions + replies = total discussions
            
            # Count unique members (people who participated)
            discussion_creators = set(CommunityDiscussion.objects.filter(topic=topic_id).values_list('id', flat=True))
            reply_creators = set(CommunityReply.objects.filter(discussion__topic=topic_id).values_list('id', flat=True))
            unique_members = len(discussion_creators.union(reply_creators))  # Unique participants
            
            topic_stats[topic_id] = {
                'title': topic_name,
                'discussions': total_discussions
            }
        

        return Response(topic_stats)
    except Exception as e:

        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def discussions(request, discussion_id=None):
    """Handle discussions CRUD operations"""
    if request.method == 'GET':
        topic = request.GET.get('topic')
        if topic:
            discussions = CommunityDiscussion.objects.filter(topic=topic).order_by('created_at')
        else:
            discussions = CommunityDiscussion.objects.all().order_by('created_at')
        
        data = []
        for discussion in discussions:
            data.append({
                'id': discussion.id,
                'topic': discussion.topic,
                'title': discussion.title,
                'content': discussion.content,
                'created_at': discussion.created_at,
                'replies_count': discussion.replies.count()
            })
        
        return Response(data)
    
    elif request.method == 'POST':
        try:
            topic = request.data.get('topic')
            title = request.data.get('title')
            content = request.data.get('content')
            
            if not all([topic, title, content]):
                return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
            
            discussion = CommunityDiscussion.objects.create(
                topic=topic,
                title=title,
                content=content,
                is_anonymous=True
            )
            
            return Response({
                'id': discussion.id,
                'message': 'Discussion created successfully'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    elif request.method == 'PUT':
        try:
            discussion = CommunityDiscussion.objects.get(id=discussion_id)
            discussion.title = request.data.get('title', discussion.title)
            discussion.content = request.data.get('content', discussion.content)
            discussion.save()
            return Response({'message': 'Discussion updated successfully'})
        except CommunityDiscussion.DoesNotExist:
            return Response({'error': 'Discussion not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        try:
            discussion = CommunityDiscussion.objects.get(id=discussion_id)
            discussion.delete()
            return Response({'message': 'Discussion deleted successfully'})
        except CommunityDiscussion.DoesNotExist:
            return Response({'error': 'Discussion not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def discussion_replies(request, discussion_id):
    """Get replies for a discussion or add new reply"""
    try:
        discussion = CommunityDiscussion.objects.get(id=discussion_id)
    except CommunityDiscussion.DoesNotExist:
        return Response({'error': 'Discussion not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        replies = discussion.replies.all().order_by('created_at')
        data = []
        for reply in replies:
            data.append({
                'id': reply.id,
                'content': reply.content,
                'created_at': reply.created_at,
                'is_anonymous': reply.is_anonymous
            })
        
        return Response(data)
    
    elif request.method == 'POST':
        try:
            content = request.data.get('content')
            if not content:
                return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            reply = CommunityReply.objects.create(
                discussion=discussion,
                content=content,
                is_anonymous=True
            )
            
            return Response({
                'id': reply.id,
                'message': 'Reply added successfully'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT', 'DELETE'])
@permission_classes([AllowAny])
def reply_operations(request, reply_id):
    """Handle reply edit and delete operations"""
    try:
        reply = CommunityReply.objects.get(id=reply_id)
    except CommunityReply.DoesNotExist:
        return Response({'error': 'Reply not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        try:
            reply.content = request.data.get('content', reply.content)
            reply.save()
            return Response({'message': 'Reply updated successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        try:
            reply.delete()
            return Response({'message': 'Reply deleted successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
