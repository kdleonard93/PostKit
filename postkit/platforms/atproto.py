from atproto import Client, models
import time

class ATProtoPublisher:
    def __init__(self, credentials):
        self.handle = credentials['handle']  # e.g., "username.bsky.social"
        self.password = credentials['password']  # App password
        self.client = None
    
    def authenticate(self):
        """Login once, works for all AT Protocol apps"""
        self.client = Client()
        self.client.login(self.handle, self.password)
    
    def post_thread(self, chunks, image_path=None):
        """
        Post a thread:
        1. First post (with optional image)
        2. Replies to first post
        3. Each reply references root and parent
        """
        posts = []
        parent_ref = None
        root_ref = None
        
        for i, chunk in enumerate(chunks):
            if i == 0:
                # First post
                if image_path:
                    # Upload image
                    with open(image_path, 'rb') as f:
                        img_data = f.read()
                    blob = self.client.upload_blob(img_data)
                    
                    # Create post with image
                    embed = models.AppBskyEmbedImages.Main(
                        images=[models.AppBskyEmbedImages.Image(
                            alt="",
                            image=blob.blob
                        )]
                    )
                    post = self.client.send_post(text=chunk, embed=embed)
                else:
                    post = self.client.send_post(text=chunk)
                
                # Set references
                root_ref = models.create_strong_ref(post)
                parent_ref = models.create_strong_ref(post)
            else:
                # Reply to previous post
                reply_ref = models.AppBskyFeedPost.ReplyRef(
                    parent=parent_ref,
                    root=root_ref
                )
                post = self.client.send_post(text=chunk, reply_to=reply_ref)
                parent_ref = models.create_strong_ref(post)
            
            posts.append(post)
            
            if i < len(chunks) - 1:
                time.sleep(1)
        
        return self.post_thread_with_hashtags(chunks, image_path, hashtags=None)
    
    def publish(self, content):
        """
        Publish to all AT Protocol apps
        Returns: {'Bluesky': True, 'Flashes': True, 'Skylight': True,'Pinksky': True}
        """
        self.authenticate()
        
        results = {}
        
        try:
            thread = content['thread'].copy()
            hashtags = content.get('hashtags', [])
            
            if hashtags and thread:
                hashtag_text = ' '.join(hashtags)
                first_chunk = thread[0]
                
                if len(first_chunk) + len(hashtag_text) + 2 <= 300:
                    thread[0] = f"{first_chunk}\n\n{hashtag_text}"
            
            self.post_thread_with_hashtags(thread, content['image'], hashtags)
            
            results['Bluesky'] = True
            results['Flashes'] = True
            results['Skylight'] = True
            results['Pinksky'] = True
            
        except Exception as e:
            print(f"AT Protocol error: {e}")
            results['Bluesky'] = False
            results['Flashes'] = False
            results['Skylight'] = False
            results['Pinksky'] = False
        
        return results
    
    def post_thread_with_hashtags(self, chunks, image_path=None, hashtags=None):
        """
        Post a thread with proper hashtag facets
        """
        posts = []
        parent_ref = None
        root_ref = None
        
        for i, chunk in enumerate(chunks):
            # Create facets for hashtags in this chunk
            facets = []
            if hashtags and i == 0:  # Only process hashtags in first post
                facets = self.create_hashtag_facets(chunk, hashtags)
            
            if i == 0:
                # First post
                if image_path:
                    # Upload image
                    with open(image_path, 'rb') as f:
                        img_data = f.read()
                    blob = self.client.upload_blob(img_data)
                    
                    # Create post with image and facets
                    embed = models.AppBskyEmbedImages.Main(
                        images=[models.AppBskyEmbedImages.Image(
                            alt="",
                            image=blob.blob
                        )]
                    )
                    post = self.client.send_post(text=chunk, embed=embed, facets=facets if facets else None)
                else:
                    post = self.client.send_post(text=chunk, facets=facets if facets else None)
                
                # Set references
                root_ref = models.create_strong_ref(post)
                parent_ref = models.create_strong_ref(post)
            else:
                # Reply to previous post
                reply_ref = models.AppBskyFeedPost.ReplyRef(
                    parent=parent_ref,
                    root=root_ref
                )
                post = self.client.send_post(text=chunk, reply_to=reply_ref)
                parent_ref = models.create_strong_ref(post)
            
            posts.append(post)
            
            if i < len(chunks) - 1:
                time.sleep(1)
        
        return posts

    def create_hashtag_facets(self, text, hashtags):
        """
        Create facets for hashtags to make them clickable
        
        Example: "#python #coding" becomes clickable tags
        """
        facets = []
        
        for tag in hashtags:
            # Remove # if present
            clean_tag = tag.lstrip('#')
            search_tag = f"#{clean_tag}"
            
            # Find where this hashtag appears in the text
            start_pos = text.find(search_tag)
            if start_pos != -1:
                # Calculate byte positions (AT Protocol uses UTF-8 byte positions)
                byte_start = len(text[:start_pos].encode('utf-8'))
                byte_end = len(text[:start_pos + len(search_tag)].encode('utf-8'))
                
                # Create the facet
                facet = models.AppBskyRichtextFacet.Main(
                    features=[models.AppBskyRichtextFacet.Tag(tag=clean_tag)],
                    index=models.AppBskyRichtextFacet.ByteSlice(
                        byteStart=byte_start,
                        byteEnd=byte_end
                    )
                )
                facets.append(facet)
        
        return facets if facets else None