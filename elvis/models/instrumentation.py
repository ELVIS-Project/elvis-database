from elvis.models.elvis_model import ElvisModel


class InstrumentVoice(ElvisModel):
    class Meta:
        ordering = ["title"]
        app_label = "elvis"

    def solr_dict(self):
        instrument_voice = self

        return {'type': 'elvis_instrument_voice',
                'id': int(instrument_voice.id),
                'name': instrument_voice.name,
                'instruments_voices_searchable': instrument_voice.name,
                'created': instrument_voice.created,
                'updated': instrument_voice.updated,
                'comment': instrument_voice.comment}
