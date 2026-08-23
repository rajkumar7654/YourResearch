from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain



def run_search_pipeline(topic: str) -> dict:
    
    state = {}
    
    #Step - 1 search agent working
    print("\n"+" ="*50)
    print("Search agnet is working... ")
    print("="*50)
    
    search_agent = build_search_agent()
    search_results = search_agent.invoke({
        "messages": [("user", f"Find recent and reliable and detailed information about: {topic}")]
    })
    state["search_results"] = search_results['messages'][-1].content
    print("\nSearch Results:", state["search_results"])
    

    
    #Step - 2 reader agent working
    print("\n"+" ="*50)
    print("Reader agent is working... ")
    print("="*50)
    
    reader_agent = build_reader_agent()

    reader_result = reader_agent.invoke({
        "messages": [
            (
                "user",
                f"Based on the following search results about '{topic}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{state['search_results'][:800]}"
            )
        ]
    })

    state['scraped_content'] = reader_result['messages'][-1].content

    print("\nScraped content:\n", state['scraped_content'])
    
    
    
    #Step - 3 writer chain working
    print("\n"+" ="*50)
    print("Writer chain is working... ")
    print("="*50)
    
    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })
    print("\n Final Report:\n", state["report"])
    
    
    #Step - 3 critic agent working
    print("\n"+" ="*50)
    print("Critic agent is working... ")
    print("="*50)
    
    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })
    
    return state



if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")
    run_search_pipeline(topic)