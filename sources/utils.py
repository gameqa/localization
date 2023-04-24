def get_new_scraper_code_boilerplate(scraperName):
    
    return f"""import cheerio from "cheerio";
import axios from "axios";
import {{ ArticleScraper, ScrapeData }} from "../interface";
import ArticleScraperBase from "../ArticleScraperBase";

export default class {scraperName}
	extends ArticleScraperBase
	implements ArticleScraper {{
	public async scrapeArticle(): Promise<ScrapeData> {{
		const {{ data, headers }} = await axios.get<string>(
			"" // TODO open up URL by creating a string literal and inject to it this.sourceArticleKey to open up the article
            // requested by the user
		);
		if (!headers['content-type'] || !headers['content-type'].includes('html')) {{
			return {{
				extract: ArticleScraperBase.REMOVE_TOKEN,
				title: ArticleScraperBase.REMOVE_TOKEN,
				sourceArticleKey: ArticleScraperBase.REMOVE_TOKEN,
				paragraphs: [ArticleScraperBase.REMOVE_TOKEN]
			}}
		}}
		const $ = cheerio.load(data);
  
        // TODO: write code to get the following instance wariables
        // - this.title (string)
        // - this.paragraphs (array of strings)
        // - this.extract (string)
        
        this.title = ""
        this.paragraphs = []
        this.extract = ""
		
		return {{
			extract: this.extract.trim(),
			title: this.title.trim(),
			sourceArticleKey: this.sourceArticleKey,
			paragraphs: this.paragraphs.map((para) => para.trim()),
		}};
	}}
}}"""