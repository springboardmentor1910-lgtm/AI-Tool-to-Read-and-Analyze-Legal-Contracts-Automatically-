# parallel_engine.py
# Module 3: Parallel Processing Implementation
# Core Engine for Multi-Domain Clause Extraction

import concurrent.futures
import time
from clues import analyze_clause_with_clues

def process_clauses_in_parallel(clauses):
    """
    Executes the clause analysis logic across multiple threads simultaneously.
    
    Args:
        clauses (list): A list of text strings (contract clauses) to analyze.
        
    Returns:
        list: A list of dictionaries containing the analysis results.
    """
    print(f"\n[System] Starting Parallel Analysis on {len(clauses)} clauses...")
    start_time = time.time()
    
    analyzed_results = []
    
    # Initialize ThreadPoolExecutor
    # max_workers is set to 4 to balance load across standard CPU cores
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        
        # Submit tasks to the executor
        # This maps the analysis function to each clause immediately
        future_to_clause = {
            executor.submit(analyze_clause_with_clues, clause): clause 
            for clause in clauses
        }
        
        # Retrieve results as they complete
        for future in concurrent.futures.as_completed(future_to_clause):
            try:
                result = future.result()
                # Filter out generic operations if necessary, or keep all
                if result:
                    analyzed_results.append(result)
            except Exception as e:
                print(f"[Error] Failed to process clause: {e}")
            
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"[System] Parallel Execution Complete. Time: {execution_time:.4f}s")
    
    return analyzed_results

# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    # Real-world data structure test
    real_contract_data = [
        "The Vendor shall pay a penalty of $500 for delays.",
        "This agreement is governed by the laws of Texas.",
        "Data must be encrypted according to GDPR standards.",
        "Server uptime must be maintained at 99.9%.",
        "Payment is due within 30 days of invoice receipt.",
        "The supplier acts as an independent contractor.",
        "Audit logs must be retained for 5 years.",
        "Support team will respond within 4 hours."
    ]
    
    # Execute engine
    findings = process_clauses_in_parallel(real_contract_data)
    
    # Output results
    print("\n--- EXTRACTED FINDINGS ---")
    for finding in findings:
        print(f"[{finding['agent']}] {finding['analysis']}")