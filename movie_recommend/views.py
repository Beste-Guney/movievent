import math
from moviechoose.models import Movie, Ratings
from nltk import word_tokenize
from nltk.corpus import stopwords
from unidecode import unidecode
import string
import random
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy.spatial.distance import euclidean


def pre_process(corpus):
    # convert input corpus to lower case.
    corpus = corpus.lower()

    # collecting a list of stop words from nltk and punctuation form
    # string class and create single array.
    stopset = stopwords.words('english') + list(string.punctuation)

    # remove stop words and punctuations from string.
    # word_tokenize is used to tokenize the input corpus in word tokens.
    corpus = " ".join([i for i in word_tokenize(corpus) if i not in stopset])

    # remove non-ascii characters
    corpus = unidecode(corpus)
    return corpus


def finding_distances(overview):
    corpus = []
    movies = Movie.objects.all()
    movie_ids = []
    movie_overview = [overview]

    for m in movies:
        movie_ids.append(m.id)
        corpus.append(m.overview)

    vector_overviews = TfidfVectorizer()
    features = vector_overviews.fit_transform(corpus).todense()
    transformed_overview = vector_overviews.transform(movie_overview).todense()

    distances = []

    index = 0
    for f in features:
        distance = euclidean_distances(transformed_overview, f)
        id_distance = (movie_ids[index], distance)
        distances.append(id_distance)
        index = index + 1

    return distances


def get_recommended_movies(request):
    # lists
    fav_movies = []
    movie_list = []
    recommended_movies = []
    all_movies = Movie.objects.all()
    ratings = Ratings.objects.filter(rater=request.user)

    for mov in all_movies:
        movie_list.append(mov)

    for r in ratings:
        if r.score >= 4:
            fav_movies.append(r.movie)

    for f in fav_movies:
        print(f.title)

    if not fav_movies:
        recommended_movies = random.sample(movie_list, 5)
        return recommended_movies

    for mov in fav_movies:
        distances = finding_distances(mov.overview)

        for d in distances:
            if d[0] != mov.id and d[1] <= 1.30:
                movie = Movie.objects.get(id=d[0])
                recommended_movies.append(movie)
    if len(recommended_movies) > 15:
        recommended_movies = random.sample(recommended_movies,15)

    return recommended_movies


def k_means_movie(user):
    scaler = StandardScaler()
    array = []
    labels = []

    # filtering ratings
    rate = Ratings.objects.filter(rater=user)

    for r in rate:
        movie = r.movie
        labels.append(movie.id)
        array_item = [movie.genre, movie.release_date, r.score]
        array.append(array_item)

    scaled_movies = scaler.fit_transform(array)
    kmeans = KMeans(init='k-means++', n_clusters=3, n_init=10, max_iter=300, random_state=42)
    movie_clusters = kmeans.fit(scaled_movies).labels_

    cluster_labels = [[] for i in range(3)]
    for i, j in enumerate(movie_clusters):
        cluster_labels[j].append(labels[i])

    return movie_clusters, kmeans, cluster_labels


def k_means_my_implementation(user):
    number_of_clusters = 3
    clusters = [[], [], []]
    centroid_points = []
    change = True

    # generating centroids
    for i in range(number_of_clusters):
        x, y, z = random.randint(1, 50), random.randint(1930, 2020), random.randint(0, 6)
        item = [x, y, z]
        centroid_points.append(item)

    # creating movie data
    array = []
    labels = []

    # filtering ratings
    rate = Ratings.objects.filter(rater=user)

    for r in rate:
        movie = r.movie
        array_item = [movie.id, movie.genre, int(movie.release_date), r.score]
        array.append(array_item)

    while change:
        change = False

        clusters = [[], [], []]
        for item in array:
            array_item = [item[1], item[2], item[3]]
            closest_centroid_index = find_minimum(centroid_points[0], centroid_points[1],
                                                  centroid_points[2], array_item)[2]
            clusters[closest_centroid_index].append(item)

        for i in range(number_of_clusters):
            if clusters[i]:
                middle = calculate_middle_point(clusters[i])
                if centroid_points[i] != middle:
                    centroid_points[i] = middle
                    change = True

    for i in clusters:
        array_item = []
        for j in range(len(i)):
            movie_item = i[j][0]
            array_item.append(movie_item)

        labels.append(array_item)

    return labels, centroid_points


def calculate_middle_point(cluster):
    middle_point_x, middle_point_y, middle_point_z = 0, 0, 0

    for i in range(len(cluster)):
        middle_point_x = middle_point_x + cluster[i][1]
        middle_point_y = middle_point_y + cluster[i][2]
        middle_point_z = middle_point_z + cluster[i][3]

    return [(middle_point_x/len(cluster)), (middle_point_y/len(cluster)), (middle_point_z/len(cluster))]


def calculate_distance(coordinate1, coordinate2):
    return math.sqrt((coordinate1[0] - coordinate2[0])**2 + (coordinate1[1] - coordinate2[1])**2 +
                     (coordinate1[2] - coordinate2[2])**2)


def find_minimum(center1, center2, center3, point):
    minimum_distance = calculate_distance(center1, point)
    closest_centroid = center1
    index = 0

    if calculate_distance(center2, point) < minimum_distance:
        if calculate_distance(center3, point) < calculate_distance(center2, point):
            minimum_distance = calculate_distance(center3, point)
            closest_centroid = center3
            index = 2
        else:
            minimum_distance = calculate_distance(center2, point)
            closest_centroid = center2
            index = 1

    return minimum_distance, closest_centroid, index


def get_distance_between_centers(center1, center2, labels2, number_of_clusters):
    minimum_distance = 1000000000000000000000000000
    minimum_index = 0
    matching_cluster_labels = []
    occupied = []

    for i in range(number_of_clusters):
        for j in range(number_of_clusters):
            if calculate_distance(center1[i], center2[j]) < minimum_distance:
                if j not in occupied:
                    minimum_index = j
                    minimum_distance = calculate_distance(center1[i], center2[j])

        matching_cluster_labels.append(labels2[minimum_index])
        occupied.append(minimum_index)

        minimum_distance = 100000000000000000000
    return matching_cluster_labels


def get_distance_between_clusters(cluster1, cluster2, labels2, number_of_clusters):
    minimum_distance = 100000000000000000000
    minimum_index = 0
    centers_1 = cluster1.cluster_centers_
    centers_2 = cluster2.cluster_centers_
    matching_cluster_labels = []
    occupied = []

    for i in range(number_of_clusters):
        for j in range(number_of_clusters):
            c1 = centers_1[i].reshape(-1, 1)
            c2 = centers_2[j].reshape(-1, 1)

            if euclidean(c1, c2) < minimum_distance:
                if j not in occupied:
                    minimum_index = j
                    minimum_distance = euclidean(c1, c2)

        matching_cluster_labels.append(labels2[minimum_index])
        occupied.append(minimum_index)

        minimum_distance = 100000000000000000000
    return matching_cluster_labels



# Create your views here.
# class MovieRecommendationView(View):
#     def get(self, request):
#
#         # lists
#         fav_movies = []
#         movie_list = []
#         recommended_movies = []
#         all_movies = Movie.objects.all()
#         ratings = Ratings.objects.filter(rater=request.user)
#
#         for mov in all_movies:
#             movie_list.append(mov)
#
#         for r in ratings:
#             if r.score >= 4:
#                 fav_movies.append(r.movie)
#
#         for f in fav_movies:
#             print(f.title)
#         if not fav_movies:
#             recommended_movies = random.sample(movie_list, 5)
#             return render(request, 'recommendation_page.html', {'movies': recommended_movies})
#
#         for mov in fav_movies:
#             print('entered')
#             distances = finding_distances(mov.overview)
#
#             for d in distances:
#                 if d[0] != mov.id and d[1] <= 1.34:
#                     print(d[0])
#                     movie = Movie.objects.get(id=d[0])
#                     if len(recommended_movies) <= 15:
#                         recommended_movies.append(movie)
#
#         return render(request, 'slider.html', {'movies': recommended_movies})
