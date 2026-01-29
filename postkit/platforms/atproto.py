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
        
        return posts
    
    def publish(self, content):
        """
        Publish to all AT Protocol apps
        Returns: {'Bluesky': True, 'Flashes': True, 'Pinksky': True}
        """
        self.authenticate()
        
        results = {}
        
        # Bluesky: Full thread
        try:
            self.post_thread(content['thread'], content['image'])
            results['Bluesky'] = True
        except Exception as e:
            print(f"Bluesky error: {e}")
            results['Bluesky'] = False
        
        # Flashes: Summary only
        try:
            self.client.send_post(content['summary'])
            results['Flashes'] = True
        except Exception as e:
            results['Flashes'] = False
        
        # Pinksky: Full thread
        try:
            self.post_thread(content['thread'], content['image'])
            results['Pinksky'] = True
        except Exception as e:
            print(f"Pinksky error: {e}")
            results['Pinksky'] = False
        
        return results