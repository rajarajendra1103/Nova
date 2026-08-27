#!/usr/bin/env python3
"""
Nova Entity Component System - ECS (nova_libs/game/ecs.py)
Blazing-fast zero-allocation data-oriented World, Entities, Components, Systems and Queries.
"""

from typing import Any, Dict, List, Optional, Set
from nova_libs.core import StdModule


class Entity:
    def __init__(self, entity_id: int, world: 'World'):
        self.id = int(entity_id)
        self.world = world
        self.components: Dict[str, Any] = {}
        self.is_alive = True

    def add(self, comp_name: str, comp_data: Any = None):
        c_name = str(comp_name).lower()
        self.components[c_name] = comp_data if comp_data is not None else {}
        self.world._register_comp(self.id, c_name)
        return self

    def get(self, comp_name: str, default: Any = None):
        return self.components.get(str(comp_name).lower(), default)

    def set(self, comp_name: str, comp_data: Any):
        return self.add(comp_name, comp_data)

    def has(self, comp_name: str) -> bool:
        return str(comp_name).lower() in self.components

    def remove(self, comp_name: str):
        c_name = str(comp_name).lower()
        if c_name in self.components:
            del self.components[c_name]
            self.world._unregister_comp(self.id, c_name)
        return self

    def destroy(self):
        self.is_alive = False
        self.world.destroyEntity(self.id)
        return True

    def __repr__(self):
        return f"<Entity id={self.id} comps={list(self.components.keys())}>"


class Query:
    def __init__(self, world: 'World', with_comps: List[str]):
        self.world = world
        self.with_set: Set[str] = {str(c).lower() for c in with_comps}
        self.without_set: Set[str] = set()

    def without(self, without_comps: List[str]):
        for c in without_comps:
            self.without_set.add(str(c).lower())
        return self

    def entities(self) -> List[Entity]:
        res = []
        for eid, ent in self.world.entities.items():
            if not ent.is_alive: continue
            has_all = all(c in ent.components for c in self.with_set)
            has_none = not any(c in ent.components for c in self.without_set)
            if has_all and has_none:
                res.append(ent)
        return res

    def each(self, fn):
        matched = self.entities()
        for ent in matched:
            try:
                if self.world.interp: self.world.interp._invoke(fn, [ent])
                elif callable(fn): fn(ent)
            except Exception: pass
        return len(matched)


class System:
    def __init__(self, name: str, fn, query_filter: Optional[List[str]] = None):
        self.name = str(name)
        self.fn = fn
        self.query_filter = query_filter


class World:
    def __init__(self, interp=None):
        self.interp = interp
        self.entities: Dict[int, Entity] = {}
        self.systems: List[System] = []
        self._comp_index: Dict[str, Set[int]] = {}
        self._next_id = 1

    def createEntity(self) -> Entity:
        eid = self._next_id
        self._next_id += 1
        ent = Entity(eid, self)
        self.entities[eid] = ent
        return ent

    def spawn(self, *components) -> Entity:
        ent = self.createEntity()
        for c in components:
            if isinstance(c, (list, tuple)) and len(c) == 2:
                ent.add(c[0], c[1])
            elif isinstance(c, str):
                ent.add(c, {})
        return ent

    def destroyEntity(self, entity_id: int):
        eid = int(entity_id)
        if eid in self.entities:
            ent = self.entities[eid]
            ent.is_alive = False
            for c in list(ent.components.keys()):
                self._unregister_comp(eid, c)
            del self.entities[eid]
            return True
        return False

    def _register_comp(self, eid: int, comp_name: str):
        if comp_name not in self._comp_index:
            self._comp_index[comp_name] = set()
        self._comp_index[comp_name].add(eid)

    def _unregister_comp(self, eid: int, comp_name: str):
        if comp_name in self._comp_index and eid in self._comp_index[comp_name]:
            self._comp_index[comp_name].remove(eid)

    def query(self, with_components: List[str]) -> Query:
        comps = with_components if isinstance(with_components, list) else [with_components]
        return Query(self, comps)

    def addSystem(self, name: str, fn, query_filter: Optional[List[str]] = None):
        self.systems.append(System(name, fn, query_filter))
        return self

    def tick(self, dt: float = 0.016):
        for sys in self.systems:
            if sys.query_filter:
                ents = self.query(sys.query_filter).entities()
            else:
                ents = [e for e in self.entities.values() if e.is_alive]
            try:
                if self.interp: self.interp._invoke(sys.fn, [ents, dt])
                elif callable(sys.fn): sys.fn(ents, dt)
            except Exception: pass
        return len(self.systems)

    def entityCount(self) -> int:
        return len([e for e in self.entities.values() if e.is_alive])

    def clear(self):
        self.entities.clear()
        self._comp_index.clear()
        return True


def build_ecs_module(interp=None):
    _default_world = World(interp)
    m = {}

    m["world"]        = lambda: World(interp)
    m["createEntity"] = lambda: _default_world.createEntity()
    m["spawn"]        = _default_world.spawn
    m["query"]        = _default_world.query
    m["addSystem"]    = _default_world.addSystem
    m["tick"]         = _default_world.tick
    m["entityCount"]  = _default_world.entityCount
    m["clear"]        = _default_world.clear

    return StdModule("ecs", m)


# ============================================================
# C TEMPLATES (FOR COMPILER CODE GENERATION)
# ============================================================
cCode = {
    "include": '#include "nova_ecs.h"',
    "world": 'NovaWorld {var} = novaWorldNew();',
    "createEntity": 'NovaEntity {var} = novaWorldCreateEntity(&{world});',
    "spawn": 'NovaEntity {var} = novaWorldCreateEntity(&{world});',
    "tick": 'novaWorldTick(&{world}, {dt});',
    "query": 'NovaEntityList {var} = novaWorldQuery(&{world}, "{comp}");',
}
