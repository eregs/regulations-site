from django.db import models


class FailedCommentSubmission(models.Model):
    """ Model that holds comment submissions that failed when submitted to
    regulations.gov.
    """
    body = models.TextField()
