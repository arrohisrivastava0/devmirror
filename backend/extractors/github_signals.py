from datetime import datetime, timedelta, timezone

from collectors.github import fetch_github_data

def extract_github_signals(raw_data: dict)->dict:
    if raw_data is None:
        return None
    
    profile=raw_data["profile"]
    repos=raw_data["repos"]
    
    #account age in days
    created_at_raw=profile.get("account_created")
    created_at=datetime.fromisoformat(created_at_raw) if created_at_raw else None
    now=datetime.now(timezone.utc)
    
    account_age_days=(now-created_at).days if created_at else None

    #dominant language
    all_languages={}
    for repo in repos:
        for lang, bytes_count in repo["languages"].items():
            all_languages[lang]=all_languages.get(lang, 0)+bytes_count
    
    if all_languages:
        dominant_language=max(all_languages, key=all_languages.get)
        total_bytes=sum(all_languages.values())
        dominant_language_pct=all_languages[dominant_language]/total_bytes*100
        language_distribution={
            lang: round(bytes_count/total_bytes*100, 3)
            for lang, bytes_count in all_languages.items()
        }
    else:
        dominant_language="Unknown"
        dominant_language_pct=0.0
        language_distribution={}
        
    language_signals={
        "dominant_language": dominant_language,
        "dominant_language_pct": round(dominant_language_pct, 2),
        "language_distribution": language_distribution
    }
        
    #repo signals
    total_commits=0
    weak_commit_count=0
    neutral_commit_count=0
    generic_commit_count=0
    
    weak_keywords = {"fix", "update", "wip", ".", "commit",
                     "test", "temp", "minor", "changes", "misc",
                     "asdf", "asd", "stuff", "work", "done"}
    
    burst_ratio=0.0
    burst_repos=0
    
    for repo in repos:
        
        burst_commits=0
        repo_created_at_raw=repo["created_at"]
        repo_created_at=datetime.fromisoformat(repo_created_at_raw) if repo_created_at_raw else None
        burst_end_date=repo_created_at+timedelta(days=7) if repo_created_at else None
        
        #commit signals
        for commit in repo["commits"]:
            
            commit_date_raw=commit["date"]
            commit_date=datetime.fromisoformat(commit_date_raw) if commit_date_raw else None
            
            if commit_date<=burst_end_date:
                burst_commits+=1
            
            total_commits+=1
            
            message=commit["message"].strip().lower()
            if message.length<=3:
                if any(keyword in message for keyword in weak_keywords):
                    weak_commit_count+=1
                else:
                    neutral_commit_count+=1
            else:
                generic_commit_count+=1
        
        
                
    
    
                
    repo_signals={
        "total_repos": len(repos),
        "total_commits": total_commits,
        "weak_commit_count": weak_commit_count,
        "neutral_commit_count": neutral_commit_count,
        "generic_commit_count": generic_commit_count
    }

    signals={
        "account_age_days": account_age_days,
        "language_signals": language_signals,
        "repo_signals": repo_signals
    }
    return signals

if __name__ == "__main__":
    import sys
    sys.path.append("..")

    print("Fetching raw data...")
    raw = fetch_github_data("arrohisrivastava0")

    print("Extracting signals...")
    signals = extract_github_signals(raw)  