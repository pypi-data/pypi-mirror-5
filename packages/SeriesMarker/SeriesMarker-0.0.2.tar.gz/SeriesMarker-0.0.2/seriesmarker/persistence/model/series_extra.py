#==============================================================================
# -*- coding: utf-8 -*-
# 
# Copyright (C) 2013 Tobias Röttger <toroettg@gmail.com>
# 
# This file is part of SeriesMarker.
# 
# SeriesMarker is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
# 
# SeriesMarker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with SeriesMarker.  If not, see <http://www.gnu.org/licenses/>.
#==============================================================================

from seriesmarker.persistence.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer

class SeriesExtra(Base):
    """This class stores extra information about a series, e.g., its banner."""

    __tablename__ = "series_extra"

    id = Column(Integer, primary_key=True)

    series_id = Column(Integer, ForeignKey("series.id"))

    banner_id = Column(Integer, ForeignKey('banner.id'))
    banner = relationship("Banner", uselist=False)

    roles = relationship("Role")

    def __repr__(self):
        return "<SeriesExtra('%s','%s')>" % (self.id, self.series_id)


