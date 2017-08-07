"""final_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
import mode1.views as mode1
import mode2.views as mode2
import mode3.views as mode3

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^main$', mode1.ProjectMain.as_view()), #Main page of the project
    ############### MODE 1 ################
    url(r'^mode1/main$', mode1.Main.as_view()),
    url(r'^mode1/set_default$', mode1.SetDefault.as_view()),
    url(r'^mode1/edit_add_board/(?P<id>(\d)+)/(?P<mode>(\d)+)$', mode1.EditAddBoard.as_view()),
    url(r'^mode1/edit_add_transfer/(?P<id>(\d)+)/(?P<t_id>(\d)+)/(?P<mode>(\d)+)$', mode1.EditAddTransfer.as_view()),
    url(r'^mode1/view_board/(?P<id>(\d)+).{0,100}$', mode1.ViewBoard.as_view()),
    url(r'^mode1/delete_transfer/(?P<id>(\d)+)/(?P<t_id>(\d)+)$', mode1.DeleteTransfer.as_view()),
    url(r'^mode1/delete_board/(?P<id>(\d)+)$', mode1.DeleteBoard.as_view()),
    url(r'^mode1/find_shortest_game/(?P<id>(\d)+)$', mode1.FindShortestGame.as_view()),
    ############### MODE 2 ################
    url(r'^mode2/main$', mode2.Main.as_view()),
    url(r'^mode2/set_default$', mode2.SetDefault.as_view()),
    url(r'^mode2/edit_add_graph/(?P<id>(\d)+)/(?P<mode>(\d)+)$', mode2.EditAddGraph.as_view()),
    url(r'^mode2/edit_add_edge/(?P<id>(\d)+)/(?P<from_v>(\d)+)/(?P<to_v>(\d)+)/(?P<mode>(\d)+)$', mode2.EditAddEdge.as_view()),
    url(r'^mode2/delete_edge/(?P<id>(\d)+)/(?P<from_v>(\d)+)/(?P<to_v>(\d)+)$', mode2.DeleteEdge.as_view()),
    url(r'^mode2/delete_vertex/(?P<id>(\d)+)/(?P<v_id>(\d)+)$', mode2.DeleteVertex.as_view()),
    url(r'^mode2/add_vertex/(?P<id>(\d)+)', mode2.AddVertex.as_view()),
    url(r'^mode2/delete_graph/(?P<id>(\d)+)$', mode2.DeleteGraph.as_view()),
    url(r'^mode2/find_euler_path/(?P<id>(\d)+)$', mode2.FindEulerPath.as_view()),
    ############### MODE 3 ################
    url(r'^mode3/main$', mode3.Main.as_view()),

]
