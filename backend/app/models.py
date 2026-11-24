from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import UniqueConstraint

from .extensions import db
from .media_storage import media_variant_url


ID_LENGTH = 40


def cuid(prefix="c"):
    return f"{prefix}{uuid4().hex}"


def money(value):
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def storefront_locale(locale=None):
    return "zh" if locale == "zh" else "en"


def user_summary(user):
    if not user:
        return None
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
    }


class TimestampMixin:
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=lambda: cuid("usr"))
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(120))
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(32), nullable=False, default="USER")
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class VendorApplication(TimestampMixin, db.Model):
    __tablename__ = "vendor_applications"

    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=lambda: cuid("vap"))
    user_id = db.Column(db.String(ID_LENGTH), db.ForeignKey("users.id"), nullable=True, index=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    company_name = db.Column(db.String(255), nullable=False, index=True)
    contact_person = db.Column(db.String(120))
    phone = db.Column(db.String(60))
    country = db.Column(db.String(120))
    address = db.Column(db.Text)
    description = db.Column(db.Text)
    certification_files = db.Column(db.JSON, nullable=False, default=list)
    status = db.Column(db.String(32), nullable=False, default="PENDING", index=True)
    review_note = db.Column(db.Text)
    reviewed_at = db.Column(db.DateTime)

    user = db.relationship("User", backref="vendor_applications")

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "email": self.email,
            "name": self.name,
            "companyName": self.company_name,
            "contactPerson": self.contact_person,
            "phone": self.phone,
            "country": self.country,
            "address": self.address,
            "description": self.description,
            "certificationFiles": self.certification_files or [],
            "status": self.status,
            "reviewNote": self.review_note,
            "submittedAt": self.created_at.isoformat() if self.created_at else None,
            "reviewedAt": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }


class Category(TimestampMixin, db.Model):
    __tablename__ = "categories"

    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=lambda: cuid("cat"))
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    parent_id = db.Column(db.String(ID_LENGTH), db.ForeignKey("categories.id"), nullable=True)
    image = db.Column(db.String(500))
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    parent = db.relationship("Category", remote_side=[id], backref="children")
    translations = db.relationship(
        "CategoryTranslation",
        back_populates="category",
        cascade="all, delete-orphan",
        order_by="CategoryTranslation.locale",
    )
    products = db.relationship("Product", back_populates="category")

    def to_dict(self, locale=None, include_children=True, include_count=True):
        category_locale = storefront_locale(locale)
        data = {
            "id": self.id,
            "slug": self.slug,
            "parentId": self.parent_id,
            "image": self.image,
            "thumbnailUrl": media_variant_url(self.image, width=480, quality=76),
            "sortOrder": self.sort_order,
            "isActive": self.is_active,
            "translations": [t.to_dict() for t in self.translations if t.locale in ("en", "zh")],
        }
        if include_children:
            data["children"] = [
                c.to_dict(locale=category_locale, include_children=False)
                for c in sorted(self.children, key=lambda item: item.sort_order)
                if c.is_active
            ]
        if include_count:
            data["_count"] = {
                "products": len([p for p in self.products if p.status == "ACTIVE"])
            }
        picked = pick_translation(self.translations, category_locale)
        data["name"] = picked.get("name") if picked else self.slug
        data["description"] = picked.get("description") if picked else None
        return data


class CategoryTranslation(db.Model):
    __tablename__ = "category_translations"
    __table_args__ = (UniqueConstraint("category_id", "locale"),)

    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=lambda: cuid("ctr"))
    category_id = db.Column(db.String(ID_LENGTH), db.ForeignKey("categories.id"), nullable=False)
    locale = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.Text)

    category = db.relationship("Category", back_populates="translations")

    def to_dict(self):
        return {
            "id": self.id,
            "locale": self.locale,
            "name": self.name,
            "description": self.description,
            "metaTitle": self.meta_title,
            "metaDescription": self.meta_description,
        }


class Product(TimestampMixin, db.Model):
    __tablename__ = "products"

    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=lambda: cuid("prd"))
    slug = db.Column(db.String(180), unique=True, nullable=False, index=True)
    sku = db.Column(db.String(120), unique=True, nullable=False, index=True)
    status = db.Column(db.String(32), nullable=False, default="DRAFT", index=True)
    is_featured = db.Column(db.Boolean, nullable=False, default=False)
    is_new = db.Column(db.Boolean, nullable=False, default=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    compare_at_price = db.Column(db.Numeric(10, 2))
    cost_price = db.Column(db.Numeric(10, 2))
    category_id = db.Column(db.String(ID_LENGTH), db.ForeignKey("categories.id"))
    brand_name = db.Column(db.String(120))
    weight = db.Column(db.Numeric(10, 3))
    specifications = db.Column(db.JSON)
    trade_info = db.Column(db.JSON)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    vendor_id = db.Column(db.String(ID_LENGTH), db.ForeignKey("users.id"), nullable=True, index=True)
    submitted_at = db.Column(db.DateTime)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by_id = db.Column(db.String(ID_LENGTH), db.ForeignKey("users.id"), nullable=True)
    rejection_reason = db.Column(db.Text)

    category = db.relationship("Category", back_populates="products")
    vendor = db.relationship("User", foreign_keys=[vendor_id], backref="vendor_products")
    reviewed_by = db.relationship("User", foreign_keys=[reviewed_by_id], backref="reviewed_products")
    translations = db.relationship(
        "ProductTranslation",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductTranslation.locale",
    )
    images = db.relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImage.sort_order",
    )
    variants = db.relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductVariant.sort_order",
    )
    reviews = db.relationship(
        "Review",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="Review.created_at.desc()",
    )

    def to_dict(self, locale=None, include_related=False):
        approved_reviews = [review for review in self.reviews if review.is_approved]
        avg_rating = (
            sum(review.rating for review in approved_reviews) / len(approved_reviews)
            if approved_reviews
            else 0
        )
        product_locale = storefront_locale(locale)
        picked = pick_translation(self.translations, product_locale)
        return {
            "id": self.id,
            "slug": self.slug,
            "sku": self.sku,
            "status": self.status,
            "isFeatured": self.is_featured,
            "isNew": self.is_new,
            "price": money(self.price),
            "compareAtPrice": money(self.compare_at_price),
            "costPrice": money(self.cost_price),
            "brandName": self.brand_name,
            "weight": money(self.weight),
            "specifications": self.specifications or [],
            "tradeInfo": self.trade_info or {},
            "sortOrder": self.sort_order,
            "vendorId": self.vendor_id,
            "submittedAt": self.submitted_at.isoformat() if self.submitted_at else None,
            "reviewedAt": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "reviewedById": self.reviewed_by_id,
            "rejectionReason": self.rejection_reason,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "translations": [t.to_dict() for t in self.translations if t.locale in ("en", "zh")],
            "images": [image.to_dict() for image in self.images],
            "variants": [variant.to_dict() for variant in self.variants if variant.is_active],
            "category": self.category.to_dict(locale=product_locale, include_children=False)
            if self.category
            else None,
            "reviews": [review.to_dict() for review in approved_reviews],
            "_count": {"reviews": len(approved_reviews)},
            "rating": round(avg_rating, 1),
            "name": picked.get("name") if picked else self.slug,
            "description": picked.get("description") if picked else "",
            "shortDescription": picked.get("shortDescription") if picked else "",
        }

    def to_card_dict(self, locale=None):
        product_locale = storefront_locale(locale)
        picked = pick_translation(self.translations, product_locale)
        images = [image.to_dict() for image in self.images[:2]]
        variants = [variant.to_dict() for variant in self.variants if variant.is_active][:1]
        return {
            "id": self.id,
            "slug": self.slug,
            "sku": self.sku,
            "status": self.status,
            "isFeatured": self.is_featured,
            "isNew": self.is_new,
            "price": money(self.price),
            "compareAtPrice": money(self.compare_at_price),
            "brandName": self.brand_name,
            "tradeInfo": {"priceTiers": (self.trade_info or {}).get("priceTiers", [])},
            "sortOrder": self.sort_order,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "images": images,
            "image": images[0]["url"] if images else None,
            "imageThumb": images[0].get("thumbnailUrl") if images else None,
            "hoverImage": images[1]["url"] if len(images) > 1 else None,
            "hoverImageThumb": images[1].get("thumbnailUrl") if len(images) > 1 else None,
            "variants": variants,
            "category": self.category.to_dict(locale=product_locale, include_children=False, include_count=False)
            if self.category
            else None,
            "name": picked.get("name") if picked else self.slug,
            "description": picked.get("description") if picked else "",
            "shortDescription": picked.get("shortDescription") if picked else "",
        }


class ProductTranslation(db.Model):
    __tablename__ = "product_translations"
    __table_args__ = (UniqueConstraint("product_id", "locale"),)

    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=lambda: cuid("ptr"))
    product_id = db.Column(db.String(ID_LENGTH), db.ForeignKey("products.id"), nullable=False)
    locale = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    short_description = db.Column(db.String(500))
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.Text)

    product = db.relationship("Product", back_populates="translations")

    def to_dict(self):
        return {
            "id": self.id,
            "locale": self.locale,
            "name": self.name,
            "description": self.description,
            "shortDescription": self.short_description,
            "metaTitle": self.meta_title,
            "metaDescription": self.meta_description,
        }


class ProductImage(db.Model):
    __tablename__ = "product_images"

    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=lambda: cuid("pim"))
    product_id = db.Column(db.String(ID_LENGTH), db.ForeignKey("products.id"), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    alt = db.Column(db.String(255))
    sort_order = db.Column(db.Integer, nullable=False, default=0)

    product = db.relationship("Product", back_populates="images")

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "thumbnailUrl": media_variant_url(self.url, width=480, quality=78),
            "alt": self.alt,
            "sortOrder": self.sort_order,
        }


class ProductVariant(db.Model):
    __tablename__ = "product_variants"

    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=lambda: cuid("pva"))
    product_id = db.Column(db.String(ID_LENGTH), db.ForeignKey("products.id"), nullable=False)
    sku = db.Column(db.String(120), unique=True, nullable=False, index=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    compare_at_price = db.Column(db.Numeric(10, 2))
    stock = db.Column(db.Integer, nullable=False, default=0)
    low_stock_threshold = db.Column(db.Integer, nullable=False, default=5)
    options = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)

    product = db.relationship("Product", back_populates="variants")

    def to_dict(self):
        return {
            "id": self.id,
            "sku": self.sku,
            "price": money(self.price),
            "compareAtPrice": money(self.compare_at_price),
            "stock": self.stock,
            "lowStockThreshold": self.low_stock_threshold,
            "options": self.options or {},
            "isActive": self.is_active,
            "sortOrder": self.sort_order,
        }


class Review(TimestampMixin, db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=lambda: cuid("rev"))
    product_id = db.Column(db.String(ID_LENGTH), db.ForeignKey("products.id"), nullable=False)
    user_name = db.Column(db.String(120), nullable=False, default="Customer")
    rating = db.Column(db.Integer, nullable=False, default=5)
    title = db.Column(db.String(255))
    comment = db.Column(db.Text)
    images = db.Column(db.JSON)
    is_approved = db.Column(db.Boolean, nullable=False, default=True)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    helpful_count = db.Column(db.Integer, nullable=False, default=0)

    product = db.relationship("Product", back_populates="reviews")

    def to_dict(self):
        return {
            "id": self.id,
            "userName": self.user_name,
            "rating": self.rating,
            "title": self.title,
            "comment": self.comment,
            "images": self.images or [],
            "isApproved": self.is_approved,
            "isVerified": self.is_verified,
            "helpfulCount": self.helpful_count,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class Banner(TimestampMixin, db.Model):
    __tablename__ = "banners"

    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=lambda: cuid("ban"))
    position = db.Column(db.String(80), nullable=False, index=True)
    image = db.Column(db.String(500), nullable=False)
    link = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    sort_order = db.Column(db.Integer, nullable=False, default=0)

    translations = db.relationship(
        "BannerTranslation",
        back_populates="banner",
        cascade="all, delete-orphan",
        order_by="BannerTranslation.locale",
    )

    def to_dict(self, locale=None):
        picked = pick_translation(self.translations, locale)
        return {
            "id": self.id,
            "position": self.position,
            "image": self.image,
            "link": self.link,
            "isActive": self.is_active,
            "sortOrder": self.sort_order,
            "translations": [t.to_dict() for t in self.translations],
            "title": picked.get("title") if picked else None,
            "subtitle": picked.get("subtitle") if picked else None,
            "buttonText": picked.get("buttonText") if picked else None,
        }


class BannerTranslation(db.Model):
    __tablename__ = "banner_translations"
    __table_args__ = (UniqueConstraint("banner_id", "locale"),)

    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=lambda: cuid("btr"))
    banner_id = db.Column(db.String(ID_LENGTH), db.ForeignKey("banners.id"), nullable=False)
    locale = db.Column(db.String(10), nullable=False)
    title = db.Column(db.String(255))
    subtitle = db.Column(db.Text)
    button_text = db.Column(db.String(120))

    banner = db.relationship("Banner", back_populates="translations")

    def to_dict(self):
        return {
            "id": self.id,
            "locale": self.locale,
            "title": self.title,
            "subtitle": self.subtitle,
            "buttonText": self.button_text,
        }


class Subscriber(db.Model):
    __tablename__ = "subscribers"

    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=lambda: cuid("sub"))
    email = db.Column(db.String(255), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=lambda: cuid("con"))
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    reply = db.Column(db.Text)
    replied_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "subject": self.subject,
            "message": self.message,
            "isRead": self.is_read,
            "reply": self.reply,
            "repliedAt": self.replied_at.isoformat() if self.replied_at else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


class Notification(TimestampMixin, db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=lambda: cuid("ntf"))
    type = db.Column(db.String(60), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    link = db.Column(db.String(500))
    is_read = db.Column(db.Boolean, nullable=False, default=False, index=True)
    user_id = db.Column(db.String(ID_LENGTH), db.ForeignKey("users.id"), nullable=True)

    user = db.relationship("User", backref="notifications")

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "content": self.content,
            "link": self.link,
            "isRead": self.is_read,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }


class Inquiry(TimestampMixin, db.Model):
    __tablename__ = "inquiries"

    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=lambda: cuid("inq"))
    inquiry_number = db.Column(db.String(40), unique=True, nullable=False, index=True)
    user_id = db.Column(db.String(ID_LENGTH), db.ForeignKey("users.id"), nullable=True, index=True)
    status = db.Column(db.String(32), nullable=False, default="SUBMITTED", index=True)
    contact_name = db.Column(db.String(120), nullable=False)
    company_name = db.Column(db.String(160))
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(60))
    country = db.Column(db.String(120))
    quantity_requirements = db.Column(db.Text)
    customization_needs = db.Column(db.Text)
    expected_delivery_time = db.Column(db.String(120))
    message = db.Column(db.Text)

    user = db.relationship("User", backref="inquiries")
    items = db.relationship(
        "InquiryItem",
        back_populates="inquiry",
        cascade="all, delete-orphan",
        order_by="InquiryItem.id",
    )
    messages = db.relationship(
        "InquiryMessage",
        back_populates="inquiry",
        cascade="all, delete-orphan",
        order_by="InquiryMessage.created_at",
    )
    quotes = db.relationship(
        "Quote",
        back_populates="inquiry",
        cascade="all, delete-orphan",
        order_by="Quote.created_at.desc()",
    )

    def to_dict(self, include_messages=False, include_quotes=False):
        data = {
            "id": self.id,
            "inquiryNumber": self.inquiry_number,
            "userId": self.user_id,
            "status": self.status,
            "contactName": self.contact_name,
            "companyName": self.company_name,
            "email": self.email,
            "phone": self.phone,
            "country": self.country,
            "quantityRequirements": self.quantity_requirements,
            "customizationNeeds": self.customization_needs,
            "expectedDeliveryTime": self.expected_delivery_time,
            "message": self.message,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "items": [item.to_dict() for item in self.items],
        }
        if include_messages:
            data["messages"] = [message.to_dict() for message in self.messages]
        if include_quotes:
            data["quotes"] = [quote.to_dict() for quote in self.quotes]
        return data


class InquiryItem(db.Model):
    __tablename__ = "inquiry_items"

    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=lambda: cuid("iit"))
    inquiry_id = db.Column(db.String(ID_LENGTH), db.ForeignKey("inquiries.id"), nullable=False)
    product_id = db.Column(db.String(ID_LENGTH))
    variant_id = db.Column(db.String(ID_LENGTH))
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(500))
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    options = db.Column(db.JSON)
    note = db.Column(db.Text)

    inquiry = db.relationship("Inquiry", back_populates="items")

    def to_dict(self):
        return {
            "id": self.id,
            "productId": self.product_id,
            "variantId": self.variant_id,
            "name": self.name,
            "image": self.image,
            "price": money(self.price),
            "quantity": self.quantity,
            "options": self.options or {},
            "note": self.note,
        }


class Quote(TimestampMixin, db.Model):
    __tablename__ = "quotes"

    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=lambda: cuid("quo"))
    inquiry_id = db.Column(db.String(ID_LENGTH), db.ForeignKey("inquiries.id"), nullable=False, index=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    valid_until = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)

    inquiry = db.relationship("Inquiry", back_populates="quotes")
    items = db.relationship(
        "QuoteItem",
        back_populates="quote",
        cascade="all, delete-orphan",
        order_by="QuoteItem.id",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "inquiryId": self.inquiry_id,
            "totalAmount": money(self.total_amount),
            "validUntil": self.valid_until.isoformat() if self.valid_until else None,
            "notes": self.notes,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "items": [item.to_dict() for item in self.items],
        }


class QuoteItem(db.Model):
    __tablename__ = "quote_items"

    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=lambda: cuid("qit"))
    quote_id = db.Column(db.String(ID_LENGTH), db.ForeignKey("quotes.id"), nullable=False, index=True)
    product_id = db.Column(db.String(ID_LENGTH))
    variant_id = db.Column(db.String(ID_LENGTH))
    name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    options = db.Column(db.JSON)

    quote = db.relationship("Quote", back_populates="items")

    def to_dict(self):
        return {
            "id": self.id,
            "quoteId": self.quote_id,
            "productId": self.product_id,
            "variantId": self.variant_id,
            "name": self.name,
            "quantity": self.quantity,
            "unitPrice": money(self.unit_price),
            "totalPrice": money(self.total_price),
            "options": self.options or {},
        }


class InquiryMessage(db.Model):
    __tablename__ = "inquiry_messages"

    id = db.Column(db.String(ID_LENGTH), primary_key=True, default=lambda: cuid("ims"))
    inquiry_id = db.Column(db.String(ID_LENGTH), db.ForeignKey("inquiries.id"), nullable=False)
    sender_id = db.Column(db.String(ID_LENGTH), db.ForeignKey("users.id"), nullable=True, index=True)
    sender_type = db.Column(db.String(32), nullable=False, default="USER")
    content = db.Column(db.Text, nullable=False)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    inquiry = db.relationship("Inquiry", back_populates="messages")
    sender = db.relationship("User", backref="inquiry_messages")

    def to_dict(self):
        return {
            "id": self.id,
            "inquiryId": self.inquiry_id,
            "senderId": self.sender_id,
            "senderType": self.sender_type,
            "content": self.content,
            "readAt": self.read_at.isoformat() if self.read_at else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "sender": user_summary(self.sender) if self.sender else None,
        }


def pick_translation(translations, locale=None):
    if not translations:
        return None
    locale = locale or "en"
    for item in translations:
        if item.locale == locale:
            return normalize_translation(item)
    for item in translations:
        if item.locale == "en":
            return normalize_translation(item)
    return normalize_translation(translations[0])


def normalize_translation(item):
    data = item.to_dict()
    return data
