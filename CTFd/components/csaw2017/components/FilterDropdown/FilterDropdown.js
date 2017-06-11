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

    this.onClick = this.onClick.bind(this);
    this.onOutsideClick = this.onOutsideClick.bind(this);
    this.toggleShown = this.toggleShown.bind(this);
  }

  onClick(e) {
    this.toggleShown();
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
    let found = false;
    do {
      if (e.target.className.includes('filter-dropdown')) {
        found = true;
      }
      e = { target: e.target.parentNode };
    } while (e.target.parentNode);

    if (!found) {
      this.setState(state => {
        state.toggled = false;
      });
      document.removeEventListener('click', this.onOutsideClick, true);
    }
  }

  render() {
    const props = this.props;
    const { toggled } = this.state;
    const filterDropdownClasses = cn({
      'filter-dropdown': true,
      active: toggled,
      'position-left': this.props.position === 'left',
      'position-right': this.props.position === 'right'
    });
    return (
      <div className={filterDropdownClasses} onClick={this.onClick}>
        {props.title} <i className="fa fa-caret-down" />
      </div>
    );
  }
}
