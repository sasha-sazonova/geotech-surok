# Журнал установки: контур geotech-base (6.1.3) — сервер compute-node — 23.10.2026 15:42

**Хост:** Ubuntu 24.04.4, x86_64, 4 ядра (Xeon Skylake), RAM 7.6 ГБ (4.2 доступно), диск 75G/82% занят, uptime 84 дня. Python 3.12.3 системный.

**Способ:** асинхронное задание venv-base-003 (jobs-протокол 6.1.8) через стабильный маршрут mini→internal-ip. virtualenv.pyz-бандл (PEP 668 на Ubuntu 24.04 блокирует pip --user; python3-venv требует sudo, недоступен без пароля — 2 итерации failed, зафиксированы: venv-base-001 ensurepip, venv-base-002 PEP 668).

**Результат:** все 3 STEP OK (core: numpy/scipy/pandas/geoeq/pygef/groundhog/xslope/pyslope/openseespy; priority: geofound/geolysis/liquepy/pystrata/ezdxf; geo3d: gempy/geopandas/rasterio/pyproj/pyvista/ifcopenshell). Импорт-тест: 20/21 OK; единственный FAIL — тест ссылался на модуль "ags4", правильное имя импорта **python_ags4** (пакет python-ags4 1.2.0 установлен; импорт подтверждён отдельно). Итог: 21/21.

**Freeze:** envs/20261023-1542-server-geotech-base-freeze.txt (105 пакетов, снят pip freeze контура, копия на диске мини). Лог установки: logs/jobs/venv-base-003-install.log.

**Особые обстоятельства:** docker отсутствует (pip-путь); sudo недоступен (пакеты только user/venv scope); PIP_CACHE_DIR=/home/bot/geotech-jobs/.pipcache.
