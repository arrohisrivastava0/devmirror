from github import Github, GithubException, Auth
from config import GITHUB_TOKEN

def fetch_github_data(username: str)->dict:
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    
    try:
        user=g.get_user(username)
        _=user.name
        
    except GithubException as e:
        if e.status==404:
            return None
        else:
            raise e
        
    print(f"Fetching data for: {user.login}")
    print(f"Public repos: {user.public_repos}")
    
    profile={
        "username":user.login,
        "name":user.name,
        "bio":user.bio,
        "account_created":str(user.created_at),
        "followers":user.followers,
        "public_repos":user.public_repos,
    }
    
    repos_data=[]
    repos=user.get_repos(type="owner")
    
    count=0
    for repo in repos:
        if repo.fork:
            continue
        if count>=50:
            break
        
        print(f" Processing repo: {repo.name}")
        
        try:
            raw_languages=repo.get_languages()
            languages = {k: v for k, v in raw_languages.items() 
             if k.lower() != 'url' and isinstance(v, int)}
        except GithubException:
            languages={}
        
        try:
            contents=repo.get_contents("")
            root_files=[item.name.lower() for item in contents]
        except GithubException:
            root_files=[]
            
        try:
            commits=repo.get_commits()
            commit_data=[]
            
            for i, commit in enumerate(commits):
                if i>=100:
                    break
                commit_data.append({
                    "message":commit.commit.message,
                    "date":str(commit.commit.author.date),
                })
        except GithubException:
            commit_data=[]   
            
        repos_data.append({
            "name":repo.name,
            "description":repo.description,
            "topics":repo.get_topics(),
            "created_at":str(repo.created_at),
            "last_pushed":str(repo.pushed_at),
            "size_kb":repo.size,
            "stars":repo.stargazers_count,
            "forks":repo.forks_count,
            "languages":languages,
            "root_files":root_files,
            "commits":commit_data,
            "releases":repo.get_releases().totalCount,
        })   
        
        count+=1
    
    try:
        query=f"type:pr author:{username} -user:{username}" 
        external_prs=g.search_issues(query).totalCount
    except GithubException:
        external_prs=0
        
    try:
        query=f"type:issue author:{username} -user:{username}"
        external_issues=g.search_issues(query).totalCount
    except GithubException:
        external_issues=0
        
    return {
        "profile":profile,
        "repos":repos_data,
        "external_prs":external_prs,
        "external_issues":external_issues,
    } 
    
if __name__=="__main__":
    data=fetch_github_data("arrohisrivastava0")
    
    if data is None:
        print("User not found")
    else:
        print("\n--- RESULT -------------------")
        print(f"Username: {data['profile']['username']}")
        print(f"Repos fetched: {len(data['repos'])}")
        print(f"External PRs: {data['external_prs']}")
        print(f"External Issues: {data['external_issues']}")
        if data['repos']:
            print(f"First repo name: {data['repos'][0]['name']}")
            print(f"First repo languages: {data['repos'][0]['languages'] }")
            print(f"First repo root files: {data['repos'][0]['root_files'] }")