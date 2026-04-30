import asyncio
import sys
from memory.vector_store import add_to_memory, query_memory
from q_engine.ollama_client import stream_q_response

async def main():
    print(">>> 1. Injecting facts into memory...\n")

    # Push test Data
    add_to_memory(
        doc_id="axxanoid_studios_facts",
        content="Axxanoid Studios LLC is a web services and AI automation consultancy that also serves as the parent holding company (LLC) for two distinct e-commerce brands: Lagging Logic (a print-on-demand internet satire brand) and Average Stoner (an online headshop and lifestyle brand). The company is solely owned and operated by Jeremy (Axx), a senior full-stack developer with 15 years of engineering experience. While the e-commerce brands generate direct-to-consumer retail income, Axxanoid Studios itself represents the technical and B2B services arm of the business. Its operations are broken down into three main functions:1. B2B Web Services and AI Automation Rather than competing on low-cost freelance coding platforms, Axxanoid Studios positions itself as a high-ticket consultancy that solves complex business bottlenecks. Its primary B2B offerings include: AI Automation Agency (AAA) Solutions: Building custom AI tools for local businesses, such as 'AI Receptionists' (voice/text lead qualifiers integrated with CRMs) and 'Internal Knowledge Bots' (RAG pipelines that allow staff to query private company documents). The 'Technical Janitor' & Rescue Missions: Stepping in to untangle broken software architecture, fix failed AI integrations, and refactor legacy 'spaghetti code' into modern React/TypeScript stacks.High-Stakes Migrations: Acting as a 'Data Plumber' by writing custom SQL and PHP scripts to safely migrate complex e-commerce databases without corrupting customer history. Ghost Development: Serving as a white-label 'technical backstop' for SEO and marketing agencies that lack an in-house senior developer for complex custom builds. 2. The Internal 'Technical Moat' Internally, Axxanoid Studios acts as the administrative and architectural engine for its DBA brands. It builds and maintains the proprietary WordPress plugin suites, automated CI/CD deployment pipelines, and complex integrations (such as the 301 redirect bridges used to bypass social media filters) that power the e-commerce storefronts. 3. Current Strategic Status Although Axxanoid Studios is capable of executing high-ticket B2B contracts, external client work and the development of internal SaaS tools are currently treated as a 'backburner' workflow. The immediate operational focus of the company is heavily prioritized on driving 'fast cash' through Lagging Logic and Average Stoner, while Axxanoid Studios focuses on parent-company compliance, tax filings, and maintaining the core development infrastructure",
        metadata={"category": "business", "applies_to": "axxanoid_studios", "security_level": "internal"}
    )
    add_to_memory(
        doc_id="average_stoner_facts",
        content="Average Stoner is an online headshop and lifestyle brand operating as a DBA (Doing-Business-As) under the parent company Axxanoid Studios LLC. Driven by the official slogan 'Your Hustle. Your Haze. Your Elevation,' the brand seeks to actively defy the traditional 'lazy stoner' stereotype. Its target audience is the 'everyman'—including retail workers, delivery drivers, and focused professionals—who responsibly integrate cannabis into their routines for relaxation, creativity, or pain management without letting it hinder their ambitions. Core Aesthetics and Products: While it operates as a headshop, the brand encompasses a much wider lifestyle aesthetic that balances productivity with recreation: Headshop Gear & Accessories: The brand dropships functional smoking accessories, moving away from low-margin items toward high-ticket products like premium desktop vaporizers, heavy borosilicate glass, and rosin presses. Tactical EDC (Everyday Carry) Gear: High-margin dropshipped accessories designed for discretion, most notably the 'Tactical' Odor-Proof Stash Bag, which features an activated carbon lining and a combination lock to keep scents entirely off the radar. Apparel & Merch (Hosted on Lagging Logic): The brand's custom Printful apparel is sold through its sister site. This includes the flagship Average Stoner x Lagging Logic Collegiate Hoodie, the 'Smoke Smarter' anatomical brain tee, and the 'Blazed in the Haze' sweatshirt. Platform & Payment Infrastructure: Unlike Lagging Logic's Shopify setup, Average Stoner is hosted on a proprietary WordPress and WooCommerce architecture. Because it operates in the cannabis ancillary space, it relies on a bulletproof, high-risk payment gateway stack consisting of BankcardUSA, Authorize.net, and Green Check Direct to safely process transactions. High-Authority Affiliate Hub: To avoid the risks and low margins of cheap dropshipping, Average Stoner acts as an SEO-driven affiliate hub. It generates revenue through 15-20 percent commissions by publishing in-depth, high-ticket hardware reviews for brands like AirVape, Looper, and Mr. Hemp Flower via the Katalyst and Awin affiliate networks. The 301 Redirect Bridge: To safely monetize its Facebook group without triggering Meta's 'restricted content' suppression, Average Stoner routes its audience through a trusted domain link (averagestoner.com/merch-partner). This acts as a 301 redirect bridge, sending users directly to a Shopify checkout URL on Lagging Logic.",
        metadata={"category": "business", "applies_to": "average_stoner", "security_level": "internal"}
    )
    add_to_memory(
        doc_id="lagging_logic_facts",
        content="Lagging Logic is a print-on-demand (POD) and dropshipping brand built entirely around internet satire, tech-industry cynicism, and corporate burnout. The brand describes itself as making 'apparel for the chronically online' and holding a mirror to humanity's shared digital delusions. Its primary target audience consists of introverted engineers, developers, gamers, and the anti-corporate crowd who 'operate perfectly fine on high-end coffee and spite'. The brand's identity leans heavily into retro-futuristic glitch art, terminal interfaces, and 'anti-meme' humor, anchored by the official tagline, 'Fashionably late to the algorithm'. Lagging Logic'sproduct catalog is divided into specific niche categories: Satirical Apparel (generating highly searchable, relatable punchlines on tees and hoodies, such as 'Task Failed Successfully,' 'Actively Ignoring Your Slack Message,' and 'My AI Replacement Is Also Mediocre'), Desk Upgrades & 'Bed Rotting' Gear (high-margin, dropshipped gadgets that cater specifically to remote workers and 'doomscrollers'), Consumables or 'Fuel' (Functional items tailored for long coding sessions, such as Roastify dark roast coffee blends satirically named 'Runtime Error' and 'Compiler Fluid'). Platform Architecture: Lagging Logic operates its primary storefront on Shopify, but is highly integrated in to several other platforms including TikTok Shop, Meta Business, and Etsy. Pricing Strategy: The catalog is structured around three psychological pricing tiers: Tier 1 (24.99-34.99) for low-friction impulse buys like tees and mugs, Tier 2 (45.99-59.99) for aesthetic mid-tier desk gear and complex apparel, and Tier 3 (69.99-89.99+) for premium anchor tech that makes the other tiers look like a steal by comparison. Additionally, the brand employs a 'No Fat Tax' flat-pricing policy across all apparel sizes (subsidizing the cost of 2XL/3XL sizes) to build strong customer loyalty and stand out ethically. B2B Merch Hosting: Beyond its own satire lines, Lagging Logic executes a 'Merch-as-a-Service' slow-swing model. It hosts permanently open, zero-inventory digital merch booths for local businesses and bands (such as Elytra Farms and Sin Nature), handling the backend printing and fulfillment while keeping a profit margin off the top without any B2C ad spend. This multi-faceted approach allows Lagging Logic to operate as a high-margin, automated e-commerce machine that actively capitalizes on internet trends and the modern work-from-home lifestyle",
        metadata={"category": "business", "applies_to": "lagging_logic", "security_level": "internal"}
    )
    add_to_memory(
        doc_id="ui_architecture", 
        content="The UI is built with Vite, React, and TypeScript. It runs on port 5173.",
        metadata={"category": "frontend", "security_level": "internal"}
    )
    add_to_memory(
        doc_id="ai_os_architecture", 
        content="For security puropses, the Axxanoid OS is a completly custom framework not an OpenClaw pull.",
        metadata={"category": "backend", "security_level": "internal"}
    )
    # Add fiction to test metatags
    add_to_memory(
        doc_id="fake_corporate_lore",
        content="Axxanoid Studios LLC was founded by a sentient toaster in 2045.",
        metadata={"category": "lore", "security_level": "fiction"}
    )
    print("\n>>> 2. TESTING METADATA FILTERING...")
    # Don't use the exact words from the memory, ChromaDB has to figure out the meaning
    user_prompt = "What are names of Axxanoid Stuidos LLC child companies?"
    # ONLY return facts where category == business."
    strict_filter = {"category": "business"}
    print(f"Applying strict database filter: {strict_filter}")
    retrieved_context = query_memory(user_prompt, where_filter=strict_filter)
    print("Asking: {user_prompt}\n")
    
    print("\n--- WHAT WAS RETRIEVED FROM DATABASE ---")
    print(retrieved_context.strip())
    print("----------------------------------------\n")

    print(">>> 3. TESTING Q'S COMPREHENSION...\n")
    async for chunk in stream_q_response(user_prompt, system_context=retrieved_context):
        sys.stdout.write(chunk)
        sys.stdout.flush()

    print("\n" + "-" * 50)
    print(">>> Stream complete.")

if __name__ == "__main__":
    asyncio.run(main())