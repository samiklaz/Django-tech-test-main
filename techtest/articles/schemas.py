from marshmallow import validate
from marshmallow import fields
from marshmallow import Schema
from marshmallow.decorators import post_load

from techtest.articles.models import Article
from techtest.regions.models import Region
from techtest.regions.schemas import RegionSchema
from techtest.authors.models import Author
from techtest.authors.schemas import AuthorSchema


class ArticleSchema(Schema):
    class Meta(object):
        model = Article

    id = fields.Integer()
    title = fields.String(validate=validate.Length(max=255))
    content = fields.String()
    regions = fields.Method(
        required=False, serialize="get_regions", deserialize="load_regions"
    )
    authors = fields.Method(
        required=False, serialize="get_authors", deserialize="load_authors"
    )

    def get_regions(self, article):
        return RegionSchema().dump(article.regions.all(), many=True)

    def load_regions(self, regions):
        return [
            Region.objects.get_or_create(id=region.pop("id", None), defaults=region)[0]
            for region in regions
        ]
        
    def get_authors(self, article):
        return AuthorSchema().dump(article.authors.all(), many=True)

    def load_authors(self, authors):
        return [
            Author.objects.get_or_create(id=author.pop("id", None), defaults=author)[0]
            for author in authors
        ]

    @post_load
    def update_or_create(self, data, *args, **kwargs):
        regions = data.pop("regions", None)
        authors = data.pop("authors", None)
        
        article, _ = Article.objects.update_or_create(
            id=data.pop("id", None), defaults=data
        )
        if isinstance(regions, list):
            article.regions.set(regions)
        if isinstance(authors, list):
            article.authors.set(authors)
        return article
