from tennisapi.models import AtpTour


def atp_elorate(surface):
    tours = AtpTour.objects.filter(surface__icontains=surface)
    print(surface)
    for tour in tours:
        print(tour.id)
        print(tour.name)