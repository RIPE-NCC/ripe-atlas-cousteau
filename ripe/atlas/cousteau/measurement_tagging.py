from .request import AtlasRequest


class MeasurementTagRemoveRequest(AtlasRequest):
    url_path_tmpl = "/api/v2/measurements/{msm_id}/tags/{tag}/"

    def __init__(self, **kwargs):
        super(MeasurementTagRemoveRequest, self).__init__(**kwargs)
        self.msm_id = kwargs["msm_id"]
        self.tag = kwargs["tag"]
        self.url_path = self.url_path_tmpl.format(
            msm_id=self.msm_id,
            tag=self.tag
        )

    def create(self):
        return self.http_method("DELETE")


class MeasurementTagAddRequest(AtlasRequest):
    url_path_tmpl = "/api/v2/measurements/{msm_id}/tags/"

    def __init__(self, **kwargs):
        super(MeasurementTagAddRequest, self).__init__(**kwargs)
        self.tag = kwargs.pop("tag")
        self.msm_id = kwargs.pop("msm_id")
        self.url_path = self.url_path_tmpl.format(msm_id=self.msm_id)

    def _construct_post_data(self):
        self.post_data = {
            "tag": self.tag
        }

    def create(self):
        return self.post()


class MeasurementTagger(object):

    def __init__(self, **kwargs):
        self.defaults = kwargs

    def add_tag(self, msm_id, tag, **kwargs):
        req_kwargs = self.defaults.copy()
        req_kwargs.update(kwargs)
        request = MeasurementTagAddRequest(
            msm_id=msm_id, tag=tag, **req_kwargs
        )
        return request.create()

    def remove_tag(self, msm_id, tag, **kwargs):
        req_kwargs = self.defaults.copy()
        req_kwargs.update(kwargs)
        request = MeasurementTagRemoveRequest(
            msm_id=msm_id, tag=tag, **req_kwargs
        )
        return request.create()
