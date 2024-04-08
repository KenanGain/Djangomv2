from django.shortcuts import redirect, render
import requests
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Review

api_key = "c887d2e670d1e01224b4cd27ccf79d31"

from django import template

register = template.Library()

@register.filter
def humanize_money(value):
    try:
        value = int(value)
        if value < 1000000:
            return f"${value:,}"
        elif value < 1000000000:
            return f"${value / 1000000:.1f} million"
        else:
            return f"${value / 1000000000:.1f} billion"
    except (ValueError, TypeError):
        return value


# Define the base URL for TMDB API
# base_url = "https://api.themoviedb.org/3"

# # Define the movie ID you want to search
# movie_id = 11

# # Construct the URL for movie details
# url = f"{base_url}/movie/{movie_id}?api_key={api_key}"
# # Create your views here.
# def search(request):
#     query = request.GET.get('q')
#     if query:
#         # Construct the URL for searching movies with the query
        
#         response = requests.get(url)
#         if response.status_code == 200:
#             data = response.json()
#             movies = data.get('results', [])
#         else:
#             return HttpResponse("Error in fetching data from TMDB API", status=response.status_code)
#     else:
#         return HttpResponse("Please enter a search query")

#     return render(request, 'home/results.html', {
#         'data': movies  # Corrected to use string key
#     })
# def index(request):
#     return render(request, 'home/index.html')
def search(request):
    query = request.GET.get('q')
    results = []
    if query:
        # Construct the URL for searching movies with the query
        url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}"
        data = requests.get(url)
        if data.status_code == 200:
            # Parse the JSON response
            # data = response.json()
            # movies = data.get('results', [])'
            temp = []
            for m in data.json()["results"][:18]:
                if len(temp) < 3:
                    temp.append({"name":m["title"], "poster":m["poster_path"], "overview":m["overview"], "releasedate":m["release_date"], "id":m["id"] })
                else:
                    results.append(temp)
                    temp.append({"name":m["title"], "poster":m["poster_path"], "overview":m["overview"], "releasedate":m["release_date"],"id":m["id"] })
            results.append(temp) if len(temp)> 0 else None

        else:
            # Handle API errors
            return HttpResponse(f"TMDB API Error: {data.status_code}", status=data.status_code)
    else:
        # Handle case where no search query was provided
        return HttpResponse("Please enter a search query.")

    # Render the template with the list of movies
    return render(request, 'home/results.html', {
        "results": results,
        "query":query
    })

# Your index view
def index(request):
    return render(request, 'home/index.html')



def view_detail(request, id):
    tmdbdata = requests.get(f"https://api.themoviedb.org/3/movie/{id}?api_key={api_key}&language=en-US")
    # return JsonResponse(data.json())
    data = tmdbdata.json()
    
    title = data.get("title", "").replace(' ', '_')
    release_date = data.get("release_date", "")
    revenue = data.get("revenue")
    if revenue:
        new_revenue = humanize_money(revenue)
    else:
         new_revenue= "No Data"

    if title and release_date:
            release_year = release_date.split("-")[0]
            search_query = f"{title}_({release_year}_film)"
            wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_query}"
            wiki_response = requests.get(wiki_url)
            wiki_data = {}
    if wiki_response.status_code == 200:
        wiki_data = wiki_response.json()
    else:
        wiki_data = "Could not fetch details from Wikipedia for {search_query}"
    if title:
            search_query = f"{title}_(film)"
            wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_query}"
            wiki_response = requests.get(wiki_url)
            wiki_data2 = {}
    if wiki_response.status_code == 200:
        wiki_data2 = wiki_response.json()
    else:
        wiki_data = "Could not fetch details from Wikipedia for {search_query}"

    return render(request, 'home/detail.html', {
                "data": data,
                "wiki_summary": wiki_data,
                "wiki_summary2":wiki_data2,
                "revenue": new_revenue
    })
 
def review_page(request, id):
    if request.method == "POST":
        user = request.user
        review = request.POST.get("review")

        Review(review=review, user=user, movie_id=id).save()

        return redirect(f"/movie/{id}/review/")
    else:
        # return render(request, "home/review.html")
        tmdbdata = requests.get(f"https://api.themoviedb.org/3/movie/{id}?api_key={api_key}&language=en-US")
        # return JsonResponse(data.json())
        data = tmdbdata.json()
        title = data.get("title","")
        reviews = Review.objects.filter(movie_id=id)
        return render(request, "home/review.html", {
            "title": title,
            "reviews": reviews
        })