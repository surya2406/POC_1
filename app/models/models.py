from sqlalchemy import Boolean, Column,JSON,String,Text,Integer,DateTime,ForeignKey,Float,Date,Index, func
from sqlalchemy.orm import relationship
from app.db.session import Base
from datetime import datetime


class SeoTitle(Base):
    __tablename__ = "seo_title"

    id = Column(Integer, primary_key=True, index=True)
    # Reduced length from 1024 to 512 to satisfy MySQL InnoDB utf8mb4 index size limits (3072 bytes)
    Page_Url = Column(String(512), nullable=False, unique=True)
    Page_Type = Column(String(255), nullable=True)
    Primary_Keyword = Column(String(255), nullable=True)
    Secondary_Keywords = Column(Text, nullable=True)
    SEO_Optimized_Title = Column(String(255), nullable=True)
    Last_Updated = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())


class SeoKeywordsTrending(Base):
    __tablename__="seo_keywords_trending"

    id = Column(Integer, primary_key=True, index=True)
    Date = Column(Date, nullable=False, index=True)
    Category = Column(String(255), nullable=True)
    Trending_Keyword = Column(String(512), nullable=False, index=True)
    Trend_Score = Column(Float, nullable=True)
    Search_Intent = Column(String(255), nullable=True)
    Keyword_Type = Column(String(255), nullable=True)
    Platform_Source = Column(String(255), nullable=True)
    Geo_Focus = Column(String(255), nullable=True)
    Trend_Status = Column(String(100), nullable=True)
    Created_At = Column(DateTime, nullable=False, default=func.now())
    Updated_At = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())


class SeoOutcomes(Base):
    __tablename__ = "seo_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    # Reduced from 1024 to 512 to avoid exceeding utf8mb4 index byte limits
    Page_Url = Column(String(512), nullable=False)
    Original_Title = Column(String(255), nullable=True)
    Improved_Title = Column(String(255), nullable=True)
    Rationale = Column(Text, nullable=True)
    Improvement_Score = Column(Float, nullable=True)
    Issues_Found = Column(Text, nullable=True)
    Recommendations = Column(Text, nullable=True)
    Health_Score = Column(Float, nullable=True)
    Created_At = Column(DateTime, nullable=False, default=func.now())
    Updated_At = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    Index('idx_page_url', Page_Url)


class SeoHighPriority(Base):
    __tablename__ = "seo_high_priority"

    id = Column(Integer, primary_key=True, index=True)
    Outcome_Id = Column(Integer, ForeignKey("seo_outcomes.id"), nullable=False, unique=True, index=True)
    Page_Url = Column(String(512), nullable=False, index=True)
    Is_Outdated_Year = Column(Boolean, nullable=False, default=False)
    Is_Very_Low_Score = Column(Boolean, nullable=False, default=False)
    Is_Critical_Page = Column(Boolean, nullable=False, default=False)
    Priority_Score = Column(Float, nullable=True)  # Aggregated severity/urgency score
    Priority_Level = Column(String(50), nullable=False, default="high")  # e.g. high (reserved), could extend later
    Status = Column(String(50), nullable=False, default="pending")  # pending, in_progress, resolved, ignored
    Trigger_Details = Column(JSON, nullable=True)  # Stores reasons: {"outdated_year": true, "score": 22.5, ...}
    Last_Evaluated = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    Created_At = Column(DateTime, nullable=False, default=func.now())
    Updated_At = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    outcome = relationship("SeoOutcomes", backref="high_priority_flag", uselist=False)

    Index("idx_hp_page_status", Page_Url, Status)
    Index("idx_hp_priority_level", Priority_Level)


class SeoGeneratedKeywords(Base):
    __tablename__ = "seo_generated_keywords"

    id = Column(Integer, primary_key=True, index=True)
    Category = Column(String(255), nullable=False, index=True)
    Generated_Keyword = Column(String(512), nullable=False, index=True)
    Search_Intent = Column(String(100), nullable=True)  # commercial, informational, navigational, transactional
    Trend_Score = Column(Float, nullable=True)  # 0-100 trending score
    Keyword_Type = Column(String(100), nullable=True)  # primary, secondary, long_tail
    Geo_Focus = Column(String(100), nullable=True)  # global, local, regional
    Rationale = Column(Text, nullable=True)  # Why this keyword was generated
    Generation_Source = Column(String(100), nullable=False, default="ai_generated")  # ai_generated, manual, imported
    Status = Column(String(50), nullable=False, default="pending")  # pending, approved, human_edited, rejected
    Is_Active = Column(Boolean, nullable=False, default=True)  # Can be deactivated without deletion
    Performance_Score = Column(Float, nullable=True)  # Actual performance if tracked
    Last_Reviewed = Column(DateTime, nullable=True)  # When human last reviewed this keyword
    Created_At = Column(DateTime, nullable=False, default=func.now())
    Updated_At = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    Index('idx_generated_category_active', Category, Is_Active)
    Index('idx_generated_keyword_trend', Generated_Keyword, Trend_Score)
    Index('idx_generated_search_intent', Search_Intent)
    Index('idx_status', Status)
