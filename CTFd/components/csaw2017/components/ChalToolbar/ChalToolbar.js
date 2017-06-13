import Inferno from 'inferno';
import FilterDropdown from '../FilterDropdown';

import ChalProgress from '../ChalProgress';

import './ChalToolbar.scss';

export default props =>
  <div className="chal-toolbar">
    <FilterDropdown
      title="Categories"
      options={props.categories}
      filters={props.categoryFilters}
      onFilter={props.onUpdateCategoryFilters}
      position="left"
      multi
    />
    <ChalProgress total={props.totalPoints} completed={props.solvedPoints} loading={props.progressLoading} />
    <FilterDropdown
      title="Filter"
      options={props.completedOptions}
      filters={props.completedFilters}
      onFilter={props.onUpdateCompletedFilters}
      position="right"
      multi
    />
    <FilterDropdown
      title="Sort"
      options={[
        { label: <span className="icon-span">Name <i className="fa fa-sort-alpha-asc" /></span>, value: 'name_asc' },
        { label: <span className="icon-span">Name <i className="fa fa-sort-alpha-desc" /></span>, value: 'name_desc' },
        { label: <span className="icon-span">Category <i className="fa fa-sort-alpha-asc" /></span>, value: 'category_asc' },
        { label: <span className="icon-span">Category <i className="fa fa-sort-alpha-desc" /></span>, value: 'category_desc' },
        { label: <span className="icon-span">Points <i className="fa fa-sort-numeric-asc" /></span>, value: 'points_asc' },
        { label: <span className="icon-span">Points <i className="fa fa-sort-numeric-desc" /></span>, value: 'points_desc' },
      ]}
      filter={props.sortFilter}
      onFilter={props.onUpdateSortFilter}
      position="right"
    />
  </div>;
