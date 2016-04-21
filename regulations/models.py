from django.db import models


class FailedCommentSubmission(models.Model):
    """ Model that holds comment submissions that failed when submitted to
    regulations.gov. The schema is designed so that
    `regulations.tasks.submit_comment` can be easily leveraged to resubmit
    the comments.
    """
    body = models.TextField()
