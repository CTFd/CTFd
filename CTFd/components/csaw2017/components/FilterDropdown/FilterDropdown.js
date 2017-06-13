import Inferno from 'inferno';
import Component from 'inferno-component';
import cn from 'classnames';

import './FilterDropdown.scss';

export default class FilterDropdown extends Component {
  constructor(props) {
    super(props);

    this.state = {
      toggled: false
    };

    this.onDropdownClick = this.onDropdownClick.bind(this);
    this.onItemClick = this.onItemClick.bind(this);
    this.onOutsideClick = this.onOutsideClick.bind(this);
    this.toggleShown = this.toggleShown.bind(this);
  }

  onDropdownClick(e) {
    if (this.props.multi && this.state.toggled) {
      return;
    }

    let outside = false;

    do {
      if (e.target.className.includes('filter-dropdown')) {
        outside = true;
        break;
      }

      e = { target: e.target.parentNode };
    } while (e.target.parentNode);

    if (outside) {
      this.toggleShown();
    }
  }

  onItemClick(option, checked) {
    if (!this.props.multi) {
      return this.props.onFilter(option.value);
    }

    let filters = [...this.props.filters];

    if (checked) {
      filters = filters.filter(filter => filter.value !== option.value);
    } else {
      filters.push(option);
    }

    this.props.onFilter(filters);
  }

  toggleShown() {
    this.setState(state => {
      state.toggled = !state.toggled;
    });

    if (!this.state.toggled) {
      document.removeEventListener('click', this.onOutsideClick);
    } else {
      document.addEventListener('click', this.onOutsideClick);
    }
  }

  onOutsideClick(e) {
    let inside = false;

    do {
      if (e.target.className.includes('dropdown-items')) {
        inside = true;
        break;
      }

      e = { target: e.target.parentNode };
    } while (e.target.parentNode);

    if (!inside) {
      this.toggleShown();
    }
  }

  render() {
    const { title, position, options, filters, filter, multi } = this.props;
    const { toggled } = this.state;
    const filterDropdownClasses = cn({
      'filter-dropdown': true,
      active: toggled,
      multi,
      'position-left': position === 'left',
      'position-right': position === 'right'
    });
    return (
      <div className={filterDropdownClasses} onClick={this.onDropdownClick}>
        {title} <i className={'fa fa-caret-' + (toggled ? 'up' : 'down')} />
        <div className="dropdown-items">
          {options.map(option => {
            const checked = multi ? filters.map(f => f.value).includes(option.value) : filter === option.value;

            return (
              <div
                className={'dropdown-item' + (!multi && checked ? ' active' : '')}
                key={option.value}
                onClick={this.onItemClick.bind(null, option, checked)}
              >
                {option.label}
                {multi &&
                  <label className="check"><input type="checkbox" checked={checked} /><div className="box" /></label>}
              </div>
            );
          })}
        </div>
      </div>
    );
  }
}

FilterDropdown.defaultProps = {
  options: [],
  filters: []
};
