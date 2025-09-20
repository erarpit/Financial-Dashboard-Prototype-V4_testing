from typing import Dict, List, Optional
import logging
from datetime import datetime
from models.domain import Sector, Industry
from models.schemas import SectorData, IndustryData, DomainOverview, TopCompany, ResearchReport

logger = logging.getLogger(__name__)

class DomainService:
    """Service for managing financial domains (sectors, industries)"""
    
    def __init__(self):
        self.sectors = {
            "technology": Sector("technology"),
            "healthcare": Sector("healthcare"),
            "finance": Sector("finance"),
            "energy": Sector("energy"),
            "consumer": Sector("consumer"),
            "industrial": Sector("industrial"),
            "materials": Sector("materials"),
            "utilities": Sector("utilities"),
            "real_estate": Sector("real_estate"),
            "communication": Sector("communication")
        }
        
        self.industries = {
            "software": Industry("software"),
            "pharmaceuticals": Industry("pharmaceuticals"),
            "banking": Industry("banking"),
            "oil_gas": Industry("oil_gas"),
            "retail": Industry("retail"),
            "automotive": Industry("automotive"),
            "mining": Industry("mining"),
            "electric_utilities": Industry("electric_utilities"),
            "reit": Industry("reit"),
            "telecom": Industry("telecom")
        }
    
    def get_sector(self, sector_key: str) -> Optional[SectorData]:
        """Get sector data by key"""
        try:
            if sector_key not in self.sectors:
                logger.warning(f"Sector {sector_key} not found")
                return None
            
            sector = self.sectors[sector_key]
            
            # Convert to SectorData schema
            top_companies = []
            if sector.top_companies is not None:
                for idx, row in sector.top_companies.iterrows():
                    top_companies.append(TopCompany(
                        symbol=idx,
                        name=row.get('name', ''),
                        rating=row.get('rating'),
                        market_weight=row.get('market weight')
                    ))
            
            research_reports = []
            for report in sector.research_reports or []:
                research_reports.append(ResearchReport(
                    title=report.get('title', ''),
                    url=report.get('url', ''),
                    date=report.get('date', '')
                ))
            
            return SectorData(
                key=sector.key,
                name=sector.name,
                symbol=sector.symbol,
                overview=DomainOverview(**sector.overview),
                top_companies=top_companies,
                research_reports=research_reports,
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error getting sector {sector_key}: {str(e)}")
            return None
    
    def get_industry(self, industry_key: str) -> Optional[IndustryData]:
        """Get industry data by key"""
        try:
            if industry_key not in self.industries:
                logger.warning(f"Industry {industry_key} not found")
                return None
            
            industry = self.industries[industry_key]
            
            # Convert to IndustryData schema
            top_companies = []
            if industry.top_companies is not None:
                for idx, row in industry.top_companies.iterrows():
                    top_companies.append(TopCompany(
                        symbol=idx,
                        name=row.get('name', ''),
                        rating=row.get('rating'),
                        market_weight=row.get('market weight')
                    ))
            
            research_reports = []
            for report in industry.research_reports or []:
                research_reports.append(ResearchReport(
                    title=report.get('title', ''),
                    url=report.get('url', ''),
                    date=report.get('date', '')
                ))
            
            return IndustryData(
                key=industry.key,
                name=industry.name,
                symbol=industry.symbol,
                overview=DomainOverview(**industry.overview),
                top_companies=top_companies,
                research_reports=research_reports,
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error getting industry {industry_key}: {str(e)}")
            return None
    
    def get_all_sectors(self) -> List[SectorData]:
        """Get all available sectors"""
        sectors = []
        for sector_key in self.sectors.keys():
            sector_data = self.get_sector(sector_key)
            if sector_data:
                sectors.append(sector_data)
        return sectors
    
    def get_all_industries(self) -> List[IndustryData]:
        """Get all available industries"""
        industries = []
        for industry_key in self.industries.keys():
            industry_data = self.get_industry(industry_key)
            if industry_data:
                industries.append(industry_data)
        return industries
    
    def get_sector_companies(self, sector_key: str, limit: int = 10) -> List[TopCompany]:
        """Get top companies in a sector"""
        sector_data = self.get_sector(sector_key)
        if not sector_data:
            return []
        
        return sector_data.top_companies[:limit]
    
    def get_industry_companies(self, industry_key: str, limit: int = 10) -> List[TopCompany]:
        """Get top companies in an industry"""
        industry_data = self.get_industry(industry_key)
        if not industry_data:
            return []
        
        return industry_data.top_companies[:limit]
    
    def search_domains(self, query: str) -> Dict[str, List[str]]:
        """Search for sectors and industries matching query"""
        query_lower = query.lower()
        
        matching_sectors = [
            key for key in self.sectors.keys() 
            if query_lower in key.lower() or query_lower in self.sectors[key].name.lower()
        ]
        
        matching_industries = [
            key for key in self.industries.keys() 
            if query_lower in key.lower() or query_lower in self.industries[key].name.lower()
        ]
        
        return {
            "sectors": matching_sectors,
            "industries": matching_industries
        }

# Global instance
domain_service = DomainService()
